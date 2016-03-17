#encoding=utf-8

import networkx as nx
from networkx import utils
import ConfigParser
import matplotlib.pyplot as plt
import random
import math
import time
import csv

TeamList=[]
# globals(day)

def CreateGraph(data):
#parameters:
#  type:
#     erdos renyi
#     watts strogatz
#     barabasi albert
#     powerlaw cluster
#  data:
#    n : int
#    The number of nodes
#    k : int
#    Each node is joined with its ``k`` nearest neighbors in a ring topology.
#    p : float
#    The probability of rewiring each edge
#    seed : int, optional
#    Seed for random number generator (default=None)
#    m : int
#    Number of edges to attach from a new node to existing nodes
    type=data[0][1]
    n=int(data[1][1])
    p=float(data[2][1])
    if data[3][1]=='None':
        seed=data[3][1]
    else:
        seed=int(data[3][1])
    k=int(data[4][1])
    m=int(data[5][1])

    if type=='er':
        G=nx.random_graphs.erdos_renyi_graph(n, 0.2, seed)

    elif type=='ws':
        G=nx.random_graphs.watts_strogatz_graph(n, 6, 0.3, seed)

    elif type=='ba':
        G=nx.random_graphs.barabasi_albert_graph(n, 2, seed)

    elif type=='regular':
        G=nx.random_graphs.random_regular_graph(3, n, seed)

    return G

# def GenSkill(data):
# #    return Return n lists of sequence from a power law distribution.
#     n=int(data[0][1])
#     exponent=float(data[1][1])
# #     numlist=[]
#     numlist=utils.powerlaw_sequence(n,exponent)
#     numlist.sort(reverse=True)
#
#     for i,num in enumerate(numlist):
#
#         if num<int(num)+0.5:
#             numlist[i]=int(num)
#         elif num>=int(num)+0.5:
#             numlist[i]=int(num)+1
#     print "1-----------------------------"
#     print numlist
#     max=numlist[0]
#     all=range(max)
# #    print all
#     for j,num1 in enumerate(numlist):
#         a=random.SystemRandom()
# #         print a
#         numlist[j]=a.sample(all,num1)
#     print " 2---------------------------"
#     print numlist
#     return numlist

def GenSkillForPerson():
    personsSkillList = []
    for person in range(int(conf.items('Person')[0][1])):
        personSkill = []
        distributionRange = range(0,11,1)
        a=random.SystemRandom()
        for i in range(10):
            #从[0,10]区间随机产生一个整数
            randomNum = a.sample(distributionRange,1)[0]
            personSkill.append(randomNum)
        personsSkillList.append(personSkill)
    print('========================为开发者们设定知识背景===========================')
    print(personsSkillList[0])
    print('========================为开发者们设定知识背景===========================')
    print
    return personsSkillList

def GenSkillForProject():
    projectSkillDemandList = []
    numList = range(0,1001,1)
    a=random.SystemRandom()
    for project in range(int(conf.items('Task')[0][1])):
        projectSkill = []
        for i in range(10):
            randomNum = a.sample(numList,1)[0]
            projectSkill.append(randomNum)
        projectSkillDemandList.append(projectSkill)
    print('=========================为项目设定知识需求===============================')
    print(projectSkillDemandList[0])
    print('=========================为项目设定知识需求===============================')
    print
    return projectSkillDemandList

def ToBusy(i,person,tasknum):
    person['status']='occupied'
    person['task'].append(tasknum)
    person['start'] = day
    print '%s is assigned to project %s in day %s'%(i,tasknum,day)

# 计算个体和项目匹配的技能数量
def hasSameSkill(person,task):
    temp = []
    for t in range(10):
        temp.append(int(task[1]['skill'][t]/100))

    j = 0
    for i in range(10):
        if person['skill'][i] != 0 and task[1]['skill'][i] != 0:
            j+=1

    return j



def AssignTask(task,network):

    Team={'member':[]}

    #找出匹配度最高的个体
    theFirst = findTheMatchest(network,task)

    ToBusy(theFirst,network.node[theFirst],task[0])

    task[1]['status']='processing'
    Team['member'].append(theFirst)
    Team['task'] = task[0]
    Team['speed'] = [0,0,0,0,0,0,0,0,0,0]

    # 从邻域中找匹配度大于零的个体加入team
    for node in network.neighbors(theFirst):

        if network.node[node]['status']=='available' and hasSameSkill(network.node[node],task) and len(Team['member'])<task[1]['limit']:
            ToBusy(node,network.node[node],task[0])
            Team['member'].append(node)

    TeamList.append(Team)
    return Team

# 选出匹配度最高成员的id
def findTheMatchest(network,task):
    arr = []
    theBest = 0
    for i in range(500):
        if network.node[i]['status'] == 'occupied':
            continue
        numOfSameSkill = hasSameSkill(network.node[i],task)
        if numOfSameSkill>theBest:
            theBest = numOfSameSkill
    for j in range(500):
        if network.node[i]['status'] == 'occupied':
            continue
        if theBest == hasSameSkill(network.node[j],task):
            return j



def addMember(task,network):

    Team = searchTeam(task[0])
    if len(Team['member'])>task[1]['limit']:
        return Team
    else:
        for m in Team['member']:
            for node in network.neighbors(m):
                if network.node[node]['status']=='available' and hasSameSkill(network.node[node],task) and len(Team['member'])<task[1]['limit']:
                    ToBusy(node,network.node[node],task[0])
                    Team['member'].append(node)
                    return Team

#根据taskID找到负责该项目的team
def searchTeam(taskId):
    for team in TeamList:
        if team['task'] == taskId:
            return team



def do():
    # -*- coding: UTF-8 -*-
    print '============================================================='
    print '============= start the simulation of CI ===================='
    print '============================================================='
    print 'initializing......'
    print

    #生成四种网络类型
    G=CreateGraph(conf.items('Graph'))
    # pos = nx.spectral_layout(G)
    # nx.draw(G,pos,node_size = 100)
    # plt.show()

    #初始化开发者的知识背景
    PersonSkill = GenSkillForPerson()


    #初始化开发项目的知识需求
    ProjectsSkill = GenSkillForProject()

    ProjectsList=[]

    #对开发者和项目进行初始化

    for j,skill in enumerate(ProjectsSkill):

        #skill是对十项技能的知识需求;limit是项目限定的人员数量;money是资金成本;time是时间成本;status是任务状态;start是开始时间;end是结束时间

        temp=[j,{'skill':skill,'limit':10,'money':0,'time':0,'status':'undone','start':0,'end':0}]
        ProjectsList.append(temp)
    print '=================================================================='
    print '                           ProjectsList'
    print '=================================================================='
    for project in ProjectsList:
        print project

    print


    for i,node in enumerate(G.node):
        G.node[i]['skill']= PersonSkill[i]
        G.node[i]['salary']=sum(PersonSkill[i])*100
        G.node[i]['task']=[]
        G.node[i]['status']='available'
        # 对每个个体设定开始时间和结束时间
        G.node[i]['start'] = 0
        G.node[i]['end'] = 0
    print '============================these are developers==============================='
    print G.node
    print '============================these are developers==============================='
    print


    #=======================================================================
    # assign and process tasks
    #=======================================================================

    count=0
    global day
    day = 0

    while 1:

        day +=1
        print '============================================================='
        print '                          day%s                              '%(day)
        print '============================================================='

        #==========================团队组建=======================
        for num,project in enumerate(ProjectsList):
            if project[1]['status'] == 'undone':
                #给项目第一次匹配开发者
                AssignTask(ProjectsList[num],G)
                ProjectsList[num][1]['start'] = day


            if project[1]['status'] == 'processing':
                #没达到人员上限的情况下,每天增加一个member
                addMember(ProjectsList[num],G)



        rmlist = []
        # print G.node
        # print G.node[0]['skill']

        # 开发ing...  ...
        for team in TeamList:
             #任务知识需求列表
             skilllist = ProjectsList[team['task']][1]['skill']
             #计算任务负责团队的作业速度
             for mem in team['member']:
                 for s in range(10):
                    team['speed'][s] = team['speed'][s] + G.node[mem]['skill'][s]
             countSkill = 0
             for skill in skilllist:
                 if skill > 0:
                     countSkill+=1

             if countSkill>0:
                 for skillnum in range(10):
                     ProjectsList[team['task']][1]['skill'][skillnum]-=team['speed'][skillnum]
             else:
                 print('++++++++++++++++++++++TASK IS FINISHED')
                 print team
                 rmlist.append(team)
                 print'----------------------------'


        print('+++++++++++++++++++++TEAMLIST')
        for t in TeamList:
            print t

        print '+++++++++++++++rmLIST'
        for r in rmlist:
            print r

        #结算待移除任务列表中项目的时间成本和资金成本,恢复项目负责团队成员的状态为available
        for dtsk in rmlist:
            count+=1
            TeamList.remove(dtsk)
            teamcost=0
            tms=dtsk['member']
            for p in tms:
                G.node[p]['status']='available'
                G.node[p]['end'] = day
                teamcost += (G.node[p]['end']-G.node[p]['start'])*G.node[p]['salary']/30

            ProjectsList[dtsk['task']][1]['end']=day
            ProjectsList[dtsk['task']][1]['time']=ProjectsList[dtsk['task']][1]['end']-ProjectsList[dtsk['task']][1]['start']
            ProjectsList[dtsk['task']][1]['money']=teamcost
            ProjectsList[dtsk['task']][1]['status']='done'
            print 'task %s is done!!!'%(dtsk['task'])
            print  ProjectsList[dtsk['task']]
            print 'it costs %s people %s days and %s rmb'%(len(tms),ProjectsList[dtsk['task']][1]['time'],ProjectsList[dtsk['task']][1]['money'])
            print '---------------'
#       #计算平均时间成本和资金成本
        if len(TeamList)==0:
            print '========================================================================'
            print '============= end the simulation and show the results =================='
            print '========================================================================'
            print TeamList
            total_time=0
            total_money=0
            for i in ProjectsList:
                total_money+=i[1]['money']
                total_time+=i[1]['time']
            if count==len(ProjectsList):
                print 'the alltasks are done!!!!! '
                print 'it takes %s days and %s rmb in totol'%(day,total_money)
                print 'it takes %s days and %s rmb in average'%(float(total_time)/float(count),total_money/float(count))
            else:
                print '%s of %s tasks is done,the rest of tasks cannot find a match.'%(count,len(ProjectsList))
                print 'it takes %s days and %s rmb in totol'%(day,total_money)
                print 'it takes %s days and %s rmb in average'%(float(total_time)/float(count),total_money/float(count))
            csvfile=open('distribution.csv','a')
            line='%s,%s,%s,%s,%s,%s,%s,%s'%(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),len(G.node),len(ProjectsList),count,day,total_money,float(total_time)/float(count),total_money/float(count))
            csvfile.write(line+'\n')
            csvfile.close()
            break

def expriment(data):
    numOfExpri = 0
    number = data[0][1]
    for num in range(int(number)):
        do()
        numOfExpri +=1
    return numOfExpri


#=================================================================
#                            主程序入口
#==================================================================
if __name__=='__main__':
    conf = ConfigParser.ConfigParser()
    conf.read('conf.cfg')
    # numdo为反复实验的次数
    numdo = expriment(conf.items('Expriment'))
    print('expriment has run %s times in all'%(numdo))