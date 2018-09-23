# geppetto
A framework for training and operating continuously learning robots 

...UNDER CONSTRUCTION...
The big idea is to put together a continuously learning robot. 
Obviously the real interest here is trying to do continuous mostly 
unsupervised learning in a grounded environment. Learning objectives
will probably include likelihood of sensor information (video, audio, proximity)
as well as maybe a higher level objective like altering the environment to decrease
entropy. 

Server: the learning is happening on a server with GPU.

Robot: the robot has a minimal OS (raspbian probably) the uses web sockets to 
send sensor information and receive control information. 

