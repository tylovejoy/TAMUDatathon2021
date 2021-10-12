import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd

env = RobotorqueEnv()
s = env.reset()

fig, ax = plt.subplots()
def animate(i):
    ax.clear()
    ax.set_xlabel('time (s)')
    ax.set_ylabel('mm')
    robot_posn = env.bolt.x
    env.step(robot_posn)
    pd.DataFrame(env.history).set_index('time').drop(['theta', 'bolt lin acc'], axis=1).plot(ax=ax)

ani = animation.FuncAnimation(fig, animate, interval=200)
plt.show()