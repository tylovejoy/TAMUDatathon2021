# Robotorque

[Watch intro video here](youtube.com)

### Introduction
Here at GM manafacturing, we love finding innovative ways to solve hard problems.
On the Vision as a Service (VaaS) Team, our specialty is computer vision and robotics.
Today, you have the chance to solve a real problem we are working on, called Robotorque.

### Problem Definition
The use case of Robotorque is to be able to screw bolts in on a moving fixture using a robot arm.
At each timestep, we take a 3d picture of the fixture of interest using a lidar.
Our goal is to be able to use the image
input to be able to control the robot to move to the bolt and screw it in.
This problem could theoretically be solved in an end-to-end solution (perhaps using reinforcement learning).
If you think you can do this, go right ahead!
However, another common approach is to divide this problem into two stages.
First, try to estimate the pose (rotation and translation) of the bolt, and then move the 
robot to match the pose.

We leave it up to you to solve these problems: stage 1 is pose estimation and stage 2 is robot control. 
In stage 1, you will be given an RGB-depth image of a bolt that has been transformed.
Your goal is to estimate the pose of that bolt based off the image.
In stage 2, we expose a simulator endpoint which streams RGB-depth images. On our backend, we are transforming
the bolt according to physical simulation models that are hidden to you. For each image, you must return
where you want the robot to go. Your goal is to keep the robot arm touching the face of the bolt. You
are rewarded accordingly. The catch is this: your observation cadence is much less frequent than your control cadence.
That is, you must control the robot based off where you predict the bolt is at any time.
The seperation between stage 1 and stage 2 is just to help you break down the problem. 
In the end, you will only be judged based off your performance on stage 2.


## How do I win?
At any time during the competition, you are allowed to submit your solution to our backend and we
will automatically grade you. You can query for the highscores and see where you stand. 

If your team is the top N scores (N TBD) at the end of the competition, 
your team will be asked to give a presentation to the GM judges.
The final prizes will be chosen according to the GM judges' discretion based on a
combination of final score and how much we like your solution. :)

We will also give an honorable mention to those teams which have the highest stage1 score.


## Resources
- [Tranformation Matrix](https://en.wikipedia.org/wiki/Transformation_matrix)
- [Open3d](http://www.open3d.org/docs/release/introduction.html)
 

## How to get started
We have provided starter code along with a baseline solution to part 1 and part 2.
Please make sure to register yourself USING YOUR DISCORD USERNAME.
Please also have everyone on your team post in the *General Motors* discord channel
that you are working on this challenge.
Running the example code will submit the baseline solution under your username
and will enter you into the contest.

### Demo
Open [this google colab](https://colab.research.google.com/drive/1jCrbcQwIKktIp0ea_v_4kHsZ71vmoaiK#scrollTo=Ux0rXpz1i8T7)
for a really short demo. However, we recommend not using colab for this challenge and instead doing it locally... its just better.

## Quick start
To get started locally, run the following on your local machine (assuming your have conda installed):
```
git clone gm-datathon.github.com
cd gm-datathon
conda create -n gm-env python=3.8
conda activate gm-env 
pip install -r requirements.txt
python pose_estimation.py YOUR_DISCORD_NAME
python robot_control.py YOUR_DISCORD_NAME
python scoring_client.py YOUR_DISCORD_NAME
```
Feel free to check out the notebooks for some more examples and starter code!