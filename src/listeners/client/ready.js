const { Listener } = require('@eartharoid/dbf');
const ms = require('ms');
const sync = require('../../lib/sync');
const checkForUpdates = require('../../lib/updates');
const { isStaff } = require('../../lib/users');
const {
	ActionRowBuilder,
	ButtonBuilder,
	ButtonStyle,
} = require('discord.js');
const ExtendedEmbedBuilder = require('../../lib/embed');
const {
	getAverageTimes,
	sendToHouston,
} = require('../../lib/stats');

module.exports = class extends Listener {
	constructor(client, options) {
		super(client, {
			...options,
			emitter: client,
			event: 'ready',
			once: true,
		});
	}

	async run() {
		/** @type {import("client")} */
		const client = this.client;

		// process.title = `"[Discord Tickets] ${client.user.tag}"`; // too long and gets cut off
		process.title = 'tickets';
		client.log.success('Connected to Discord as "%s" over %d shards', client.user.tag, client.ws.shards.size);

		await client.initAfterLogin();

		// fill cache
		await sync(client);

		if (process.env.PUBLISH_COMMANDS === 'true') {
			client.log.info('Automatically publishing commands...');
			client.commands.publish()
				.then(commands => client.log.success('Published %d commands', commands?.size))
				.catch(client.log.error);
		}

		await client.application.fetch();
		if (process.env.PUBLIC_BOT === 'true' && !client.application.botPublic) {
			client.log.warn('The `PUBLIC_BOT` environment variable is set to `true`, but the bot is not public.');
		} else if (process.env.PUBLIC_BOT !== 'true' && client.application.botPublic) {
			client.log.warn('Your bot is public, but public features are disabled. Set the `PUBLIC_BOT` environment variable to `true`, or make your bot private.');
		}

		// commands are not cached automatically
		await client.application.commands.fetch();

		// presence/activity
		if (client.config.presence.activities?.length > 0) {
			let next = 0;
			const setPresence = async () => {
				client.log.verbose.cron('Updating presence');
				const cacheKey = 'cache/presence';
				let cached = await client.keyv.get(cacheKey);
				if (!cached) {
					const tickets = await client.prisma.ticket.findMany({
						select: {
							closedAt: true,
							createdAt: true,
							firstResponseAt: true,
						},
					});
					const closedTickets = tickets.filter(t => t.closedAt);
					const closedTicketsWithResponse = closedTickets.filter(t => t.firstResponseAt);
					const {
						avgResolutionTime,
						avgResponseTime,
					} = await getAverageTimes(closedTicketsWithResponse);
					cached = {
						avgResolutionTime: ms(avgResolutionTime),
						avgResponseTime: ms(avgResponseTime),
						guilds: client.guilds.cache.size,
						openTickets: tickets.length - closedTickets.length,
						totalTickets: tickets.length,
					};
					await client.keyv.set(cacheKey, cached, ms('15m'));
				}
				const activity = { ...client.config.presence.activities[next] };
				activity.name = activity.name
					.replace(/{+avgResolutionTime}+/gi, cached.avgResolutionTime)
					.replace(/{+avgResponseTime}+/gi, cached.avgResponseTime)
					.replace(/{+guilds}+/gi, cached.guilds)
					.replace(/{+openTickets}+/gi, cached.openTickets)
					.replace(/{+totalTickets}+/gi, cached.totalTickets);
				client.user.setPresence({
					activities: [activity],
					status: client.config.presence.status,
				});
				next++;
				if (next === client.config.presence.activities.length) next = 0;
			};
			setPresence();
			if (client.config.presence.activities.length > 1) setInterval(() => setPresence(), client.config.presence.interval * 1000);
		} else {
			client.log.info('Presence activities are disabled');
		}

		// stats posting
		if (client.config.stats) {
			sendToHouston(client);
			setInterval(() => sendToHouston(client), ms('12h'));
		}

		if (client.config.updates) {
			checkForUpdates(client);
			setInterval(() => checkForUpdates(client), ms('1w'));
		}

		// send inactivity warnings and close stale tickets
		const staleInterval = ms('15m');
		setInterval(async () => {
			client.log.info.cron('Handling stale tickets');
			const closeCommand = client.application.commands.cache.find(c => c.name === 'close');
			const guilds = await client.prisma.guild.findMany({
				include: {
					tickets: {
						include: { category: true },
						where: { open: true },
					},
				},
				// where: { staleAfter: { not: null } },
				where: { staleAfter: { gte: staleInterval } },
			});
			let processed = 0;
			let closed = 0;
			let marked = 0;

			for (const guild of guilds) {
				const getMessage = client.i18n.getLocale(guild.locale);
				for (const ticket of guild.tickets) {
					try {
						processed++;
						if (client.tickets.$stale.has(ticket.id)) {
							const $ = client.tickets.$stale.get(ticket.id);
							const autoCloseAfter = $.closeAt - $.staleSince;
							const halfway = $.closeAt - (autoCloseAfter / 2);
							const channel = client.channels.cache.get(ticket.id);
							if (!channel) {
								client.tickets.$stale.delete(ticket.id);
								continue;
							}
							if (Date.now() >= halfway && Date.now() < halfway + staleInterval) {
								await channel.send({
									embeds: [
										new ExtendedEmbedBuilder()
											.setColor(guild.primaryColour)
											.setTitle(getMessage('ticket.closing_soon.title'))
											.setDescription(getMessage('ticket.closing_soon.description', { timestamp: Math.floor(($.closeAt + staleInterval) / 1000) })),
									],
								});
							} else if ($.closeAt < Date.now()) {
								await client.tickets.finallyClose(ticket.id, $);
								closed++;
							}
						} else if (Date.now() - (ticket.lastMessageAt || ticket.createdAt) >= guild.staleAfter) {
						// set as stale
						/** @type {import("discord.js").TextChannel} */
							const channel = await client.channels.fetch(ticket.id);
							if (!channel) {
								await client.tickets.finallyClose(ticket.id, { reason: 'channel deleted' });
								closed++;
								continue;
							}
							const messages = (await channel.messages.fetch({ limit: 5 })).filter(m => m.author.id !== client.user.id);
							let ping = '';

							if (messages.size > 0) {
								const lastMessage =  messages.first();
								const staff = await isStaff(channel.guild, lastMessage.author.id);
								if (staff) ping = `<@${ticket.createdById}>`;
								else ping = ticket.category.pingRoles.map(r => `<@&${r}>`).join(' ');
							}

							const sent = await channel.send({
								components: [
									new ActionRowBuilder()
										.addComponents(
											new ButtonBuilder()
												.setCustomId(JSON.stringify({ action: 'close' }))
												.setStyle(ButtonStyle.Danger)
												.setEmoji(getMessage('buttons.close.emoji'))
												.setLabel(getMessage('buttons.close.text')),
										),
								],
								content: ping,
								embeds: [
									new ExtendedEmbedBuilder({
										iconURL: channel.guild.iconURL(),
										text: guild.footer,
									})
										.setColor(guild.primaryColour)
										.setTitle(getMessage('ticket.inactive.title'))
										.setDescription(getMessage('ticket.inactive.description', {
											close: `</${closeCommand.name}:${closeCommand.id}>`,
											timestamp: Math.floor((ticket.lastMessageAt || ticket.createdAt).getTime() / 1000),
										})),
								],
							});

							client.tickets.$stale.set(ticket.id, {
								closeAt: guild.autoClose ? Date.now() + guild.autoClose : null,
								closedBy: null,
								message: sent,
								messages: 0,
								reason: 'inactivity',
								staleSince: Date.now(),
							});
							marked++;
						}
					} catch (error) {
						client.log.error(error);
					}
				}
			}
			client.log.success.cron({
				closed,
				marked,
				processed,
				stale: client.tickets.$stale.size,
			});
		}, staleInterval);
	}
};
