import { RefreshingAuthProvider } from '@twurple/auth';
import { ChatClient } from '@twurple/chat';
import { promises as fs } from 'fs';
import { CLIENTID , CLIENTSECRET , CHANNEL , BITTHRESHOLD } from './nodeconfig.js';


async function main() {
    // undefined is a possible key because of anonymous gifts
    const giftCounts = new Map();
	const clientId = CLIENTID;
    const clientSecret = CLIENTSECRET;
    const tokenData = JSON.parse(await fs.readFile('./tokens.json', 'UTF-8'));
    const authProvider = new RefreshingAuthProvider(
        {
            clientId,
            clientSecret,
            onRefresh: async newTokenData => await fs.writeFile('./tokens.json', JSON.stringify(newTokenData, null, 4), 'UTF-8')
        },
        tokenData
    );
    
    const chatClient = new ChatClient({ authProvider, channels: [CHANNEL] });
    await chatClient.connect();

    chatClient.onMessage((channel, user, message, msg) => {
        if (message === '!ping'){
            chatClient.say(channel, 'Node Online')
        }
        else if (msg.isCheer) {
            const bitAmount = msg.bits
            if (bitAmount >= BITTHRESHOLD) {
                chatClient.say(channel, `!thanks ${user}`)
            }
        }
    });

    chatClient.onSub((channel, user) => {
        chatClient.say(channel, `!thanks ${user}`);
    });
    
    chatClient.onResub((channel, user, subInfo) => {
        chatClient.say(channel, `!thanks ${user}`);
    });

    chatClient.onCommunitySub((channel, user, subInfo) => {
        const previousGiftCount = giftCounts.get(user) ?? 0;
        giftCounts.set(user, previousGiftCount + subInfo.count);
        chatClient.say(channel, `!thanks ${user}`);
    });

    chatClient.onSubGift((channel, recipient, subInfo) => {
        const user = subInfo.gifter;
        const previousGiftCount = giftCounts.get(user) ?? 0;
        if (previousGiftCount > 0) {
            giftCounts.set(user, previousGiftCount - 1);
        } else {
            chatClient.say(channel, `!thanks ${user}`);
        }
    });

    chatClient.onRaid((channel, user, ChatRaidInfo) => {
        const raider = ChatRaidInfo.displayName
        const raidCount = ChatRaidInfo.viewerCount
        if (raidCount > RAIDCOUNT){
            chatClient.say(channel, `!bigthanks ${raider}`)
        }
    })
}

main();