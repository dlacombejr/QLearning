import theano
import numpy as np
from mdp import World
from deep_q_rl import DeepQLearner
from visualize import plot_weights


# define global parameters
input_width = 5
input_height = 5
n_actions = 4
discount = 0.9
learn_rate = .01
batch_size = 100
rng = np.random
replay_size = 1000
max_iter = 1000
epsilon = 0.2

# generate the world
world = World()

# initialize replay memory D <s, a, r, s', t>
D = (
    np.zeros((replay_size, 1, input_height, input_width), dtype=theano.config.floatX),
    np.zeros((replay_size, 1), dtype='int32'),
    np.zeros((replay_size, 1), dtype=theano.config.floatX),
    np.zeros((replay_size, 1, input_height, input_width), dtype=theano.config.floatX),
    np.zeros((replay_size, 1), dtype='int32')
)
s1 = np.zeros((1, 1, input_height, input_width), dtype=theano.config.floatX)
s1[0, 0, 1, 1] = 1
terminal = 0
state = s1
for step in range(replay_size):

    print(step)

    action = np.random.randint(4)
    state_prime, reward, terminal = world.act(state, action)
    sequence = [state, action, reward, state_prime, terminal]

    for entry in range(len(D)):

        D[entry][step] = sequence[entry]

    if terminal == 0:
        state = state_prime
    elif terminal == 1:
        state = s1

# build the reinforcement-learning agent
agent = DeepQLearner(
    input_width,
    input_height,
    n_actions,
    discount,
    learn_rate,
    batch_size,
    rng
)

# begin training
state = s1  # initialize first state
running_loss = []
for i in range(max_iter):

    action = agent.choose_action(state, epsilon)  # choose an action using epsilon-greedy policy
    state_prime, reward, terminal = world.act(state, action)  # get the new state, reward and terminal value from world
    sequence = [state, action, reward, state_prime, terminal]  # concatenate into a sequence

    for entry in range(len(D)):

        np.delete(D[entry], 0, 0)  # delete the first entry along the first axis
        np.append(D[entry], sequence[entry])  # append the new sequence at the end

    batch_index = np.random.permutation(batch_size)  # get random mini-batch indices

    loss = agent.train(D[0][batch_index], D[1][batch_index], D[2][batch_index], D[3][batch_index], D[4][batch_index])
    running_loss.append(loss)

    print("Loss at iter %i: %f" % (i, loss))

    if terminal == 0:
        state = state_prime
    elif terminal == 1:
        state = s1

# test to see if it has learned best route
state = s1
terminal = 0
path = np.zeros((5, 5))
path += state[0, 0, :, :]
i = 0
while terminal == 0:

    action = agent.choose_action(state, 0)
    state_prime, reward, terminal = world.act(state, action)
    state = state_prime

    print("Reward: %f" % reward)
    path += state[0, 0, :, :]

    i += 1

print(path)

# visualize the weights for each of the action nodes
weights = agent.get_weights()
print(weights)
print(weights.shape)

plot_weights(weights)
