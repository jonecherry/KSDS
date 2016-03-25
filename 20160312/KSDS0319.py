#encoding=utf-8

import networkx as nx
from networkx import utils
import ConfigParser
# import matplotlib.pyplot as plt
import random
import math
import time
import csv

TeamList=[]
conf1 = ConfigParser.ConfigParser()
conf1.read('conf.cfg')
switchbutton = int(conf1.items('Expriment')[2][1])

def CreateGraph(data):


    n=NodeNum
    # p=float(data[2][1])
    if data[3][1]=='None':
        seed=data[3][1]
    else:
        seed=int(data[3][1])
    # k=int(data[4][1])
    # m=int(data[5][1])

    if type=='er':
        G=nx.random_graphs.erdos_renyi_graph(n, p, seed)

    elif type=='ws':
        G=nx.random_graphs.watts_strogatz_graph(n, m_ws, 0.5, seed)

    elif type=='ba':
        G=nx.random_graphs.barabasi_albert_graph(n, m_ba, seed)

    elif type=='regular':
        G=nx.random_graphs.random_regular_graph(m_re, n, seed)

    return G

def GenSkillForPerson():
    personsSkillList = []
    for person in range(PersonNum):
        personSkill = []
        distributionRange = range(0,11,1)
        a=random.SystemRandom()
        for i in range(10):
            #从[0,10]区间随机产生一个整数
            randomNum = a.sample(distributionRange,1)[0]
            personSkill.append(randomNum)
        personsSkillList.append(personSkill)
    if switchbutton == 1:
        print('========================为开发者们设定知识背景===========================')
        print(personsSkillList[0])
        print('========================为开发者们设定知识背景===========================')
        print
    return personsSkillList

def GenSkillForProject():
    projectSkillDemandList = []
    numList = range(0,11,1)
    a=random.SystemRandom()
    for project in range(ProjectNum):
        projectSkill = []
        for i in range(10):
            randomNum = a.sample(numList,1)[0]
            projectSkill.append(randomNum)
        projectSkillDemandList.append(projectSkill)
    if switchbutton == 1:
        print('=========================为项目设定知识需求===============================')
        print(projectSkillDemandList[0])
        print('=========================为项目设定知识需求===============================')
        print
    return projectSkillDemandList

def ToBusy(i,person,tasknum):
    person['status']='occupied'
    person['task'].append(tasknum)
    person['start'] = day
    if switchbutton == 1:
        print '%s is assigned to project %s in day %s'%(i,tasknum,day)


# 返回技能匹配的数量,匹配规则:当集合相同位置的技能的值相近(差的绝对值小于等于1),就存在一个技能匹配
# def MatchDegree1(person,task):
#     j = 0
#     for i in range(10):
#         if abs(person['skill'][i]- task[1]['skill'][i]) < 1:
#             j +=1
#     return j

# 返回技能匹配的数量,匹配规则:当人的技能值大于等于项目的技能值,就存在一个技能匹配
def MatchDegree2(person,task):
    j = 0
    for i in range(10):
        if task[1]['principals'][i] == -2 :
            continue
        if person['skill'][i] - task[1]['skill'][i] >= 0:
            j +=1
    return j
# 团队组建初期，返回Team
def AssignTask(task,network):

    Team={'member':[]}

    # 项目第一次匹配个体,只要匹配度大于等于1就可以
    if Match(network,task) != 'notfound':
        theFirst = Match(network,task)
        ToBusy(theFirst,network.node[theFirst],task[0])

        task[1]['status']='processing'
        Team['member'].append(theFirst)
        Team['task'] = task[0]

        # 从邻域中找匹配度大于等于1的个体加入team
        for node in network.neighbors(theFirst):
            if network.node[node]['status']=='available' and MatchDegree2(network.node[node],task) and len(Team['member'])<int(task[1]['limit']):
                ToBusy(node,network.node[node],task[0])
                Team['member'].append(node)

        TeamList.append(Team)
        return Team
    else:
        return 'waiting'
# 返回一个匹配度大于1的个体
def Match(network,task):

    for i in range(PersonNum):
        if network.node[i]['status'] == 'available' and MatchDegree2(network.node[i],task)>=1:
            return i
    return 'notfound'
# 选出匹配度最高成员的id
def findTheMatchest(network,task):
    arr = []
    theBest = 0
    conf = ConfigParser.ConfigParser()
    conf.read('conf.cfg')


    for i in range(int(conf.items('Graph')[1][1])):
        if network.node[i]['status'] == 'occupied':
            continue
        numOfSameSkill = MatchDegree2(network.node[i],task)
        if numOfSameSkill>theBest:
            theBest = numOfSameSkill
    for j in range(int(conf.items('Graph')[1][1])):
        if network.node[j]['status'] == 'occupied':
            continue
        if theBest == MatchDegree2(network.node[j],task):
            return j


# 项目执行过程中，继续找匹配度大于等于1的个体
def addMember(task,network):

    Team = searchTeam(task[0])
    if len(Team['member'])>task[1]['limit']:
        return Team
    else:
        for m in Team['member']:
            for node in network.neighbors(m):
                if network.node[node]['status']=='available' and Team['task'] not in network.node[node]['task'] and MatchDegree2(network.node[node],task) and len(Team['member'])<int(task[1]['limit']):
                    ToBusy(node,network.node[node],task[0])
                    Team['member'].append(node)
                    return Team

#根据taskID找到负责该项目的team
def searchTeam(taskId):
    for team in TeamList:
        if team['task'] == taskId:
            return team

# team内部给成员分派任务
# param network:网络，task:项目的技能需求，team：团队
# return task:项目
def giveTaskToMember(network,task,team):

    for i in range(10):
        numfit = 0
        if task[1]['principals'][i][0] == -1 and memberWaiting(network,team)> numfit:
            theFit = fit(team,network,i)
            if theFit != 'notfound':
                numfit +=1
                task[1]['principals'][i][0] = theFit
                network.node[theFit]['status'] = 'working'
                if switchbutton == 1:
                    print '项目 %s 中,给 个体 %s : %s 分派了任务'%(task[0],theFit,network.node[theFit])


    taskUnfinish = taskUnfinished(task)
    if len(team['member'])>= 10 and isAllAssigned(task):
       for j in range(len(team['member'])):
           randomNum = random.SystemRandom().sample(taskUnfinish,1)[0]
           if network.node[j]['status'] == 'occupied':
               task[1]['principals'][randomNum].append(j)
               network.node[j]['status'] = 'working'
               if switchbutton == 1:
                   print '项目 %s 中,给 个体 %s : %s 分派了任务'%(task[0],j,network.node[j])

    return task
# 返回未完成子项目列表
def taskUnfinished(task):
    temp = []
    for i in range(10):
        if task[1]['principals'][i][0] == -2:
            continue
        else:
            temp.append(i)
    return temp

# 判断项目中的子项目是否全部有了负责人
def isAllAssigned(task):
    for i in range(10):
        if task[1]['principals'][i][0] == -1:
            return  False
    return True
# 返回team中负责第i项任务的成员id
def fit(team,network,i):
    max = 0
    for mem in team['member']:
        if network.node[mem]['skill'][i]>max and network.node[mem]['status'] == 'occupied':
            max = network.node[mem]['skill'][i]
    if max == 0:
        return 'notfound'
    else:
        temp = []
        for member in team['member']:
            if network.node[member]['skill'][i] == max and network.node[member]['status'] == 'occupied':
                temp.append(member)

        return random.SystemRandom().sample(temp,1)[0]
# 返回team中等待分派任务的成员数量
def memberWaiting(network,team):
    i = 0
    for j in team['member']:
        if network.node[j]['status'] == 'occupied':
            i +=1
    return i

# 释放成员
# param network:网络，team:团队,ProjectsList:项目列表
# return 项目
def resetMember(network,team,ProjectsList):
    workload = ProjectsList[team['task']][1]['workload']
    principals = ProjectsList[team['task']][1]['principals']
    for i in range(10):
        if workload[i]<= 0 and ProjectsList[team['task']][1]['principals'][i][0]>= 0:
            for principal in ProjectsList[team['task']][1]['principals'][i]:

                network.node[principal]['end'] = day
                network.node[principal]['status'] = 'occupied'
                # ProjectsList[team['task']][1]['money'] += (network.node[principals[i]]['end']-network.node[principals[i]]['start'])*network.node[principals[i]]['salary']/30
                if switchbutton == 1:
                    print '%s is reseted to stand by in task %s'%(principal,team['task'])
                ProjectsList[team['task']][1]['principals'][i] = [-2]

    return ProjectsList[team['task']]

def completion(projects):
    numfinished = 0
    for project in projects:
        if project[1]['status'] == 'done':
            numfinished += 1

    return numfinished

def do():
    # -*- coding: UTF-8 -*-
    print '============================================================='
    print '============= start the simulation of CI ===================='
    print '============================================================='
    print 'initializing......'
    print

    #生成四种网络类型
    G=CreateGraph(conf.items('Graph'))
    #计算网络的平均度
    degrees = nx.degree_histogram(G)
    temp = 0
    if switchbutton == 1:
        print'----------------度分布------------------'
        print degrees
        print'----------------每个节点的度-------------'
        print nx.degree(G).values()
        print
    for i in range(len(degrees)):
        temp += i*degrees[i]
    everageDegree = float(temp/float(NodeNum))
    print '======================================================='
    print '现在处于 %s 网络 ,有 %s 个节点,网络平均度为 %s'%(conf.items('Graph')[0][1],NodeNum,everageDegree)
    print '======================================================='

    # 绘制网络结构图
    # pos = nx.spectral_layout(G)
    # nx.draw(G,pos,with_labels=True,node_size = 300)
    # plt.show()

    #初始化开发者的知识背景
    PersonSkill = GenSkillForPerson()

    #初始化开发项目的知识需求
    ProjectsSkill = GenSkillForProject()

    #对开发者和项目进行初始化


    ProjectsList=[]

    for j,skill in enumerate(ProjectsSkill):
        workload = []
        for skillitem in skill:
            workload.append(skillitem*int(conf.items('Task')[2][1]))
        principals = [[-1],[-1],[-1],[-1],[-1],[-1],[-1],[-1],[-1],[-1]]
        temp=[j,{'skill':skill,'workload':workload,'limit':conf.items('Expriment')[1][1],'money':0,'time':0,'status':'undone','start':0,'end':0,'principals':principals}]
        ProjectsList.append(temp)
    if switchbutton == 1:
        print '=================================================================='
        print '                        these are projects'
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
    if switchbutton == 1:
        print '============================these are developers==============================='
        for node in G.node:
            print node
            print G.node[node]
        print '============================these are developers==============================='
        print


    #=======================================================================
    # assign and process tasks
    #=======================================================================

    count=0
    global day
    day = 0

    while 1:


        # if day > 100:
        #     break
        completionNum = completion(ProjectsList)

        rate = completionNum/float(ProjectNum)*100
        print '============================================================='
        print 'day%s      %s个人     %s个项目完成了%s个,完成百分之%s            '%(day,PersonNum,ProjectNum,completionNum,rate)
        print '============================================================='
        rateline = '%s,%s,%s,%s,%s,%s,%s'%(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),conf.items('Graph')[0][1],ProjectNum,PersonNum,everageDegree,day,rate)
        ratefile = open('rate_0325.csv','a')
        ratefile.write(rateline+'\n')
        day +=1
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
             #项目工作量
             workload = ProjectsList[team['task']][1]['workload']

             # 在team内部给member分派任务
             giveTaskToMember(G,ProjectsList[team['task']],team)

             countSkill = 0
             for skill in workload:
                 if skill > 0:
                     countSkill+=1
             # 重置完成任务的成员
             resetMember(G,team,ProjectsList)

             if countSkill>0:
                 for i in range(10):
                     principalIds  = ProjectsList[team['task']][1]['principals'][i]
                     if principalIds[0] > -1:
                         for id in principalIds:
                            ProjectsList[team['task']][1]['workload'][i] -= G.node[id]['skill'][i]
             else:
                 rmlist.append(team)
        print
        if switchbutton == 1:
            print('+++++++++++++++++++++TEAMLIST:')
            for t in TeamList:
                print '团队'
                print t
                print '项目'
                print ProjectsList[t['task']]
                # 获取符合条件的潜在成员
                print '项目%s 的潜在成员'%(t['task'])
                for m in t['member']:
                    for nb in G.neighbors(m):
                        if G.node[nb]['status'] == 'available'  and t['task'] not in G.node[nb]['task']:
                            print '%s,%s'%(nb,G.node[nb])
                print
                # print '项目%s members的邻域'%(t['task'])
                # for m in t['member']:
                #     for nb in G.neighbors(m):
                #         print '%s,%s'%(nb,G.node[nb])
            print
            print '++++++++++++++++++++++rmLIST:'
            for r in rmlist:
                print r
            print
        #结算待移除任务列表中项目的时间成本和资金成本,恢复项目负责团队成员的状态为available
        for dtsk in rmlist:
            count+=1
            TeamList.remove(dtsk)
            teamcost=0
            tms=dtsk['member']
            for tm in tms:
                G.node[tm]['end'] = day
                G.node[tm]['status'] = 'available'
                teamcost += (G.node[tm]['end']-G.node[tm]['start'])*G.node[tm]['salary']/30


            ProjectsList[dtsk['task']][1]['end']=day
            ProjectsList[dtsk['task']][1]['time']=ProjectsList[dtsk['task']][1]['end']-ProjectsList[dtsk['task']][1]['start']
            ProjectsList[dtsk['task']][1]['money']=teamcost
            ProjectsList[dtsk['task']][1]['status']='done'
            print 'task %s is done!!!'%(dtsk['task'])
            print 'it costs %s people %s days and %s rmb'%(len(tms),ProjectsList[dtsk['task']][1]['time'],ProjectsList[dtsk['task']][1]['money'])
            if switchbutton == 1:
                print  ProjectsList[dtsk['task']]
            print
#       #计算平均时间成本和资金成本
        if len(TeamList)==0:
            completionNum = completion(ProjectsList)
            rate = completionNum/float(ProjectNum)*100
            print '============================================================='
            print '现在处于 %s 网络 ,有 %s 个节点,网络平均度为 %s'%(conf.items('Graph')[0][1],NodeNum,everageDegree)

            print 'day%s      %s个人     %s个项目完成了%s个,完成百分之%s            '%(day,PersonNum,ProjectNum,completionNum,rate)
            print '========== end the simulation and show the results ==========='
            rateline = '%s,%s,%s,%s,%s,%s,%s'%(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),conf.items('Graph')[0][1],ProjectNum,PersonNum,everageDegree,day,rate)
            # ratefile = open('ws_rate_0325.csv','a')
            ratefile.write(rateline+'\n')
            total_time=0
            total_money=0
            for i in ProjectsList:
                total_money+=i[1]['money']
                total_time+=i[1]['time']
            if count==len(ProjectsList):
                print 'all tasks are done!!!!! '
                print 'it takes %s days and %s rmb in totol'%(day,total_money)
                print 'it takes %s days and %s rmb in average'%(float(total_time)/float(count),total_money/float(count))
            else:
                print '%s of %s tasks is done,the rest of tasks cannot find a match.'%(count,len(ProjectsList))
                print 'it takes %s days and %s rmb in totol'%(day,total_money)
                print 'it takes %s days and %s rmb in average'%(float(total_time)/float(count),total_money/float(count))
            csvfile=open('ever_0325.csv','a')
            line='%s,%s,%s,%s,%s,%s,%s,%s,%s'%(type,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),len(G.node),everageDegree,len(ProjectsList),day,total_money,float(total_time)/float(count),total_money/float(count))
            csvfile.write(line+'\n')
            csvfile.close()
            ratefile.close()
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
    PersonNum = int(conf.items('Person')[0][1])
    ProjectNum = int(conf.items('Task')[0][1])
    p = 0.006
    m_ws = 6
    m_ba = 3
    m_re = 6

    typeList = ['er','ws','ba','regular']
    for type in typeList:
        # 考察网络结构对于完成率的影响
        # NodeNum = PersonNum
        # numdo = expriment(conf.items('Expriment'))
        # print('expriment has run %s times in all'%(numdo))

        #考察节点数的影响
        # for i in range(10):
        #     PersonNum += 50
        #     NodeNum = PersonNum
        #     # numdo为反复实验的次数
        #     numdo = expriment(conf.items('Expriment'))
        #     print('expriment has run %s times in all'%(numdo))


        #  考察平均度的影响
        for j in range(1):
            p += 0.005
            m_ws += 5
            m_ba += 3
            m_re += 5
            NodeNum = PersonNum
            # numdo为反复实验的次数
            numdo = expriment(conf.items('Expriment'))
            print('expriment has run %s times in all'%(numdo))

