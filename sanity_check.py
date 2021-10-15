# Just make sure everything installed correctly
import open3d
import numpy
import matplotlib
import nptyping
import tqdm

from utility import (pose_data, pose_estimation, remote_env,
                     scoring_client, transformation_matrix, visualizer)

print('1/5: Imports Completed Successfully')

visualizer.visualizer.draw_geometries(
    [pose_data.make_pointcloud(pose_data.get_bolt_depthimage())])

print('2/5: Visualization Completed Successfully')

# make a dummy pose estimator that submits an identity matrix 
estimator = lambda x: transformation_matrix.TransformationMatrix()
estimates = estimator(pose_estimation.test_images)
pose_estimation.make_submission(estimates)

print('3/5: Pose Estimation Completed Successfully')

# make a dummy robot controller that submits a sequence of 0 locations to go to 
controller = lambda state: numpy.zeros(remote_env.RobotorqueEnv.CONTROLS_PER_CAPTURE)
env = remote_env.RobotorqueEnv(challenge=scoring_client.Challenge.ROBOT)
state = env.reset()
done = False
while not done:
    action = controller(state)
    state, reward, done, info = env.step()

print('4/5: Robot Control Completed Successfully')

print('Pose Estimation\n', scoring_client.get_highscores(scoring_client.Challenge.POSE))
print('Robot Estimation\n', scoring_client.get_highscores(scoring_client.Challenge.ROBOT))
print('Combined Estimation\n', scoring_client.get_highscores(scoring_client.Challenge.COMBINED))

print('5/5: Scoring Queries Completed Successfully')

print('All checks complete. Sanity checked :)')