#coding=utf-8
import random

def GenSkillForPerson(person_number):
    personsSkillList = []
    for person in range(person_number):
        personSkill = []
        for i in range(10):
            randomNum = random.SystemRandom().sample([0,1],1)[0]#从[0,1]中随机产生一个整数
            personSkill.append(randomNum)
        personsSkillList.append(personSkill)
    return personsSkillList

def GenSkillForProject(project_number):
    projectSkillDemandList = []
    for project in range(project_number):
        projectSkill = []
        for i in range(10):
            randomNum = random.SystemRandom().sample([0,1],1)[0]
            projectSkill.append(randomNum)
        projectSkillDemandList.append(projectSkill)
    return projectSkillDemandList
#个体的状态有available,occupied
def init_person(G,PersonSkill):
    for i,node in enumerate(G.node):
        G.node[i]['skill']= PersonSkill[i]
        G.node[i]['project']=[]
        G.node[i]['status']='available'
        # 参与项目的开始和结束时间
        G.node[i]['start'] = 0
        G.node[i]['end'] = 0
        # 个体的分享意愿
        G.node[i]['share'] = random.SystemRandom().sample([0,1],1)[0]
        # 个体的作业效率
        # G.node[i]['rate'] = random.SystemRandom().sample(range(1,11,1),1)[0]
        G.node[i]['rate'] = 5
    return G


#项目的状态有：undone,processing,done
def init_project(ProjectsSkill):
    ProjectsList = []
    for j,skill in enumerate(ProjectsSkill):
        #随机生成每个项目的工作量，区间是100-1000
        workload = random.SystemRandom().sample(range(500,1000,1),1)[0]
        assign_limit = workload/100
        temp=[j,{'skill':skill,'workload':workload,'time':0,'status':'undone','start':0,'end':0,'assign_limit':assign_limit}]
        ProjectsList.append(temp)
    return ProjectsList