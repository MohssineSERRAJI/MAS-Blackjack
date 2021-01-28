import time
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message
from spade.template import Template
import random


class Agent1(Agent):
    class InformJuge(CyclicBehaviour):
        async def on_start(self):
            #print("agent 1 runing")
            self.value = random.randint(1, 3)
            
        async def run(self):
            #print("InformJuge from agent1 running")
            msg = await self.receive(timeout = 20)
            
            #we use str() to convert the type of msg.sender
            if msg and str(msg.sender) == "juge@jabber.lqdn.fr":
                print("[[ 1111   {} ]]".format(msg.body))
                if msg.body == "you are the winner":
                    print("[[ FROM AGENT 1 I'M THE WINNER *-* ]]")
                    self.kill(exit_code= 10)
                    return 
                
                
                self.value = random.randint(1, 3)
                msg = Message(to="juge@jabber.lqdn.fr")     # Instantiate the message
                msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
                msg.body = str(self.value)                    # Set the message content
                await self.send(msg)
                #print("Message sent from agent1!")
                # stop agent from behaviour
                #await self.agent.stop()
            else:
                print("Did not received any message after 20 seconds [[ Message from agent 1 ]]")

    async def setup(self):
        #print("Sender Agent1 started")
        b = self.InformJuge()
        template = Template()
        template.set_metadata("performative", "inform")
        self.add_behaviour(b, template)


class Agent2(Agent):
    class InformJuge(CyclicBehaviour):
        async def on_start(self):
            #print("agent 2 runing")
            self.value = random.randint(1, 3)
            
        async def run(self):
            #print("InformJuge from agent2 running")
            msg = await self.receive(timeout = 20)
            #we use str() to convert the type of msg.sender
            if msg and str(msg.sender) == "juge@jabber.lqdn.fr":
                if msg.body == "you are the winner":
                    print("[[ FROM AGENT 2 I'M THE WINNER *-* ]]")
                    self.kill(exit_code= 10)
                    return
                
                self.value = random.randint(1, 3)
                msg = Message(to="juge@jabber.lqdn.fr")     # Instantiate the message
                msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
                msg.body = str(self.value)                    # Set the message content
                await self.send(msg)
                print("Message sent from agent2!")
                # stop agent from behaviour
                #await self.agent.stop()
            else:
                print("Did not received any message after 20 seconds [[ Message from agent 2 ]]")

    async def setup(self):
        #print("Sender Agent started")
        b = self.InformJuge()
        template = Template()
        template.set_metadata("performative", "inform")
        self.add_behaviour(b, template)
        


class Juge(Agent):
    class MyBehav(CyclicBehaviour):
        async def on_start(self):
            print("Starting behaviour . . .")
            self.counterForAgent1 = 0
            self.counterForAgent2 = 0
            self.playerList = {1: "sender@jabber.lqdn.fr", 2: "myagent@jabber.lqdn.fr"}


        async def run(self):
            print("RecvBehav running")
            
            for player in self.playerList.values():
                msg = Message(to= player)                             # Instantiate the message
                msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
                msg.body = 'sender your value'              # Set the message content
                await self.send(msg)
            
            #receive messages from agents
            
            msg_rec = await self.receive(timeout=20) # wait for a message for 20 seconds
            #check if we have a winner
            if self.counterForAgent1 >= 21:
                self.kill(exit_code = 1)
                return
            elif self.counterForAgent1 >= 21:
                self.kill(exit_code = 2)
                return
            #sent process            
            elif msg_rec:
                if str(msg_rec.sender) == 'sender@jabber.lqdn.fr' :#agent 1
                    self.counterForAgent1 += int(msg_rec.body)
                if str(msg_rec.sender) == 'myagent@jabber.lqdn.fr' :#agent 2
                    self.counterForAgent2 += int(msg_rec.body)
                print("Message received with content: {} from {}".format(msg_rec.body, msg_rec.sender))
                #print('[[ {}  {} ]]'.format(self.counterForAgent1, self.counterForAgent2))
            else:
                print("Did not received any message after 20 seconds [[ Message from agent juge ]]")
        
        #at the and of the behaviour
        async def on_end(self):
            print("the winner is agent => {}".format(self.exit_code))
            msg = Message(to= self.playerList[self.exit_code], sender="juge@jabber.lqdn.fr")                             # Instantiate the message
            msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
            msg.body = 'you are the winner'             # Set the message content
            print("[[ END MESSAGE  {} ]]".format(msg))
            await self.send(msg)

    async def setup(self):
        print("Agent starting . . .")
        b = self.MyBehav()
        template = Template()
        template.set_metadata("performative", "inform")
        self.add_behaviour(b, template)





if __name__ == "__main__":
    
    agent1 = Agent1("sender@jabber.lqdn.fr", "1234567890")
    agent2 = Agent2("myagent@jabber.lqdn.fr", "1234567890")
    future = agent1.start()
    future.result() # wait for receiver agent to be prepared.
    future = agent2.start()
    future.result() # wait for receiver agent to be prepared.
    juge = Juge("juge@jabber.lqdn.fr", "1234567890")
    juge.start()

    while juge.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            juge.stop()
            agent2.stop()
            agent1.stop()
            break
    print("Agents finished")