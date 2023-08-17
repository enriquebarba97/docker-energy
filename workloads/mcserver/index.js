const mineflayer = require('mineflayer');

const { mineflayer: mineflayerViewer } = require('prismarine-viewer');

let mcData;

let mcBot;

async function collectGrass(bot, mcData) {
    // Find a nearby grass block
    const grass = bot.findBlock({
        matching: mcData.blocksByName.grass_block.id,
        maxDistance: 64,
    });

    if (grass) {
        // If we found one, collect it.
        try {
            await bot.collectBlock.collect(grass);
            collectGrass(bot, mcData); // Collect another grass block
        } catch (err) {
            console.log(err); // Handle errors, if any
        }
    }
}

const connect = () => {
    const bot = mineflayer.createBot({
        host: 'localhost',
        port: 25565,
        username: `${process.argv[2]}`,
    });

    bot.on('error', (err) => setTimeout(connect, 1e3));

    bot.loadPlugin(require('mineflayer-collectblock').plugin);

    bot.once('login', console.log);
    bot.on('chat', console.log);

    bot.once('spawn', async () => {
        mineflayerViewer(bot, { port: 3007, firstPerson: false }); // port is the minecraft server port, if first person is false, you get a bird's-eye view
        bot.chat('Hello world!');
        mcData = require('minecraft-data')(bot.version);
        collectGrass(bot, mcData);

        await bot.waitForTicks(2400);
        bot.chat("I'm done!");
        bot.quit();
        process.exit();
    });

    return (mcBot = bot);
};

connect();
