import numpy as np
import matplotlib.pyplot as plt
import pickle
import time

def CheckCondition(state,condition):
	if (np.sum(np.multiply(state, condition))-np.sum(np.multiply(condition, condition)))==0:
		return True
	else:
		return False


def CheckVisited(state,vertices):
	for i in range(len(vertices)):
		if np.linalg.norm(np.subtract(state,vertices[i]))==0:
			return True
	return False


def ComputeNextState(state, effect):
	newstate=np.add(state, effect)
	return newstate

def ComputeCost(cur_state, goal_state):
	return np.sum(abs(goal_state - cur_state)) # compare the difference

Predicates=['InHallway', 'InKitchen', 'InOffice', 'InLivingRoom', 'InGarden','InPantry','Chopped','OnRobot']

Objects=['Robot','Strawberry','Lemon', 'Paper', 'Knife'] 

nrPredicates=len(Predicates)
nrObjects=len(Objects)

ActionPre=[]
ActionEff=[]
ActionDesc=[]

###Move to hallway
for i in range(1,5,1):
	Precond=np.zeros([nrObjects, nrPredicates])
	Precond[0][0]=-1 #Robot not in hallway
	Precond[0][i]=1  #Robot in i-th room

	Effect=np.zeros([nrObjects, nrPredicates])
	Effect[0][0]=2.  #Robot in the hallway
	Effect[0][i]=-2. #Robot not in the i-th room

	ActionPre.append(Precond)
	ActionEff.append(Effect)
	ActionDesc.append("Move to InHallway from "+Predicates[i])

###Move to room
for i in range(1,5,1):
	Precond=np.zeros([nrObjects, nrPredicates])
	Precond[0][0]=1  #Robot in the hallway
	Precond[0][i]=-1 #Robot not in the ith room

	Effect=np.zeros([nrObjects, nrPredicates])
	Effect[0][0]=-2. #Robot not in the hallway
	Effect[0][i]=2.  #Robot in the ith room

	ActionPre.append(Precond)
	ActionEff.append(Effect)
	ActionDesc.append("Move to "+Predicates[i]+" from InHallway")

###ADD YOUR CODE HERE FOR THE 3 ADDITIONAL ACTIONS:

###Actions to be added:

# Move to pantry from kitchen
pantry_index = Predicates.index('InPantry')
kitchen_index = Predicates.index('InKitchen')
on_robot_index = Predicates.index('OnRobot')
knife_index = Objects.index('Knife')

for i in range(nrObjects):
	Precond=np.zeros([nrObjects, nrPredicates])
	if i != 0: #robot
		Precond[i][on_robot_index]= 1 #Object on robot
	Precond[i][kitchen_index]= 1  #Object in the kitchen
	Precond[i][pantry_index]= -1 #Object not in pantry

	Effect=np.zeros([nrObjects, nrPredicates])
	Effect[i][kitchen_index]=-2. #Object not in the kitchen
	Effect[i][pantry_index]=2  #Object in pantry

	ActionPre.append(Precond)
	ActionEff.append(Effect)
	ActionDesc.append("{} move to pantry from kitchen".format(Objects[i]))

# Move to kitchen from pantry
for i in range(nrObjects):
	Precond=np.zeros([nrObjects, nrPredicates])
	if i != 0: #robot
		Precond[i][on_robot_index]= 1 #Object on robot
	Precond[i][pantry_index]=1  #Robot in the pantry
	Precond[i][kitchen_index]=-1 #Robot not in kitchen

	Effect=np.zeros([nrObjects, nrPredicates])
	Effect[i][pantry_index]=-2. #Robot not in the pantry
	Effect[i][kitchen_index]=2  #Robot in kitchen

	ActionPre.append(Precond)
	ActionEff.append(Effect)
	ActionDesc.append("{} move to kitchen from pantry".format(Objects[i]))

# 3) Cut fruit in kitchen
chopped_index = Predicates.index('Chopped')
for fruit in ['Strawberry', 'Lemon']:
	fruit_index = Objects.index(fruit)	
	Precond=np.zeros([nrObjects, nrPredicates])
	Precond[knife_index][on_robot_index]=1
	Precond[0][kitchen_index]=1  #Robot in the kitchen
	Precond[fruit_index][kitchen_index]=1  #Fruit in the kitchen
	Precond[fruit_index][chopped_index]=-1  #Fruit is not chopped

	Effect=np.zeros([nrObjects, nrPredicates])
	Effect[fruit_index][chopped_index]=2. #Fruit is chopped

	ActionPre.append(Precond)
	ActionEff.append(Effect)
	ActionDesc.append("Robot Chop {}".format(fruit))

###Pickup object
for i in range(1,6,1):
	for j in range(1,5,1):
		Precond=np.zeros([nrObjects, nrPredicates])
		Precond[0][i]=1 #Robot in ith room
		Precond[j][i]=1 #Object j in ith room
		Precond[j][-1]=-1 #Object j not on robot

		Effect=np.zeros([nrObjects, nrPredicates])
		Effect[j][i]=-2 #Object j not in ith room
		Effect[j][-1]=2 # Object j on robot

		ActionPre.append(Precond)
		ActionEff.append(Effect)
		ActionDesc.append("Pick up "+Objects[j]+" from "+Predicates[i])
	

###Place object
for i in range(1,6,1):
	for j in range(1,5,1):
		Precond=np.zeros([nrObjects, nrPredicates])
		Precond[0][i]=1 #Robot in ith room
		Precond[j][i]=-1 #Object j not in ith room
		Precond[j][-1]=1 #Object j on robot

		Effect=np.zeros([nrObjects, nrPredicates])
		Effect[j][i]=2.  #Object j in ith room
		Effect[j][-1]=-2 #Object j not on robot

		ActionPre.append(Precond)
		ActionEff.append(Effect)
		ActionDesc.append("Place "+Objects[j]+" at "+Predicates[i])


InitialState=-1*np.ones([nrObjects, nrPredicates])
InitialState[0][0]=1 # Robot is in the hallway
InitialState[1][4]=1 # Strawberry is in the garden
InitialState[2][5]=1 # Lemon is in the pantry
InitialState[3][2]=1 # Paper is in the office
InitialState[4][2]=1 # Knife is in the office

GoalState=np.zeros([nrObjects, nrPredicates])
GoalState[0][1]=1 # Robot is in the kitchen
GoalState[1][1]=1 # Strawberry is in the kitchen
GoalState[2][4]=1 # Lemon is in the Garden
GoalState[1][6]=1 # Strawberry is chopped


np.random.seed(13)


# Search for Solution
vertices=[]
parent=[]
action=[]
cost2come=[]
vertices_bytes=[]

Queue=[]
Queue.append(0)
vertices.append(InitialState)
vertices_bytes.append(InitialState.tobytes())
parent.append(0)
action.append(-1)
MODE = "astar" #djikstra / astar
cost2come.append(0)

FoundPath=False
tic = time.time()
### Add your code here to generate path ###
while FoundPath is False:
	Queue_cost = np.array([cost2come[item] for item in Queue])
	cur_index = np.argmin(Queue_cost)
	cur_index = Queue.pop(cur_index)
	cur_path = vertices[cur_index]
	cur_cost = cost2come[cur_index]
	if MODE != "djikstra":
		goal_diff = ComputeCost(cur_path, GoalState)
	for index in range(len(ActionPre)):
		if CheckCondition(cur_path, ActionPre[index]):
			next_path = ComputeNextState(cur_path, ActionEff[index])
			next_path_bytes = next_path.tobytes()
			if next_path_bytes in vertices_bytes:
				item = vertices_bytes.index(next_path_bytes)
				if cost2come[item] > cur_cost + 1:
					cost2come[item] = cur_cost + 1
					parent[item] = cur_index
			if MODE != "djikstra":
				next_goal_diff = ComputeCost(next_path, GoalState)
			if not CheckVisited(next_path, vertices):
				vertices.append(next_path)
				vertices_bytes.append(next_path.tobytes())
				parent.append(cur_index)
				action.append(ActionDesc[index])
				if MODE == "astar":
					cost2come.append(cur_cost+1 + next_goal_diff - goal_diff)
				else:
					cost2come.append(cur_cost+1)
				Queue.append(len(vertices)-1)
			
		if CheckCondition(vertices[-1], GoalState):
			FoundPath = True
			x = Queue[-1]
			break
	# import pdb; pdb.set_trace()
# Once you've found a path, use the code below to print out your plan
print(f"FoundPath: {FoundPath}")
print("--- %s seconds ---" % (time.time() - tic))

Plan=[]
if FoundPath:
	while not x==0:
		Plan.insert(0,action[x])
		x=parent[x]
		
for i in range(len(Plan)):
	print (Plan[i])