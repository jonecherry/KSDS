#encoding=utf-8

import networkx as nx
from networkx import utils
import ConfigParser
# import matplotlib.pyplot as plt
import random
import math
import time
import csv
import chushihua

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


def ToBusy(i,person,tasknum):
    person['status']='occupied'
    person['project'].append(tasknum)
    person['start'] = day
    if switchbutton == 1:
        print '%s is assigned to project %s in day %s'%(i,tasknum,day)


# 返回技能匹配的数量,匹配规则:当人的技能值大于等于项目的技能值,就存在一个技能匹配
def MatchDegree(person,task):
    j = 0
    for i in range(10):
        if person['skill'][i] ==1 and task[1]['skill'][i] == 1:
            j +=1
    return j

# 个体选择加入收益最大化的团队
def max_payoff(node,network):
    payoff = 0
    xiangmuid = -1
    for jieidan in network.neighbors(node):
        if network.node[jieidan]['status']!='available':
            projectid =  network.node[jieidan]['project'][-1]
            shouyi_per = 0
            for team in TeamList:
                if team['task']== projectid:
                    shouyi = 0
                    group = team['members']
                    for member in group:
                        if network.node[member]['share'] ==1 and network.node[node]['share']==1:
                            shouyi = shouyi + sum(network.node[member]['skill'])
                        if network.node[member]['share'] ==1 and network.node[node]['share']==0:
                            shouyi = shouyi + sum(network.node[member]['skill'])+1
                        if network.node[member]['share'] ==0 and network.node[node]['share']==0:
                            pass
                        if network.node[member]['share'] ==0 and network.node[node]['share']==1:
                            shouyi = shouyi - 1
                    # 平均收益
                    shouyi_per = shouyi / len(group)

            if shouyi_per > payoff:
                payoff = shouyi_per
                xiangmuid = projectid

    return xiangmuid



# 团队组建初期，返回Team
def AssignTask(task,network):
    Team={'members':[]}

    # 项目第一次匹配,匹配度大于等于1就可以
    if Match(network,task) != 'notfound':
        theFirst = Match(network,task)
        ToBusy(theFirst,network.node[theFirst],task[0])

        task[1]['status']='processing'
        Team['members'].append(theFirst)
        Team['task'] = task[0]

        # 从邻域中找匹配度大于等于1，并且符合个体收益最大化的个体加入team
        for node in network.neighbors(theFirst):
            if network.node[node]['status']=='available' and MatchDegree(network.node[node],task) and task[0] == max_payoff(node,network):
                ToBusy(node,network.node[node],task[0])
                Team['members'].append(node)

        TeamList.append(Team)
        return Team
    else:
        return 'waiting'
# 返回一个匹配度大于1的个体
def Match(network,task):
    for i in range(PersonNum):
        if network.node[i]['status'] == 'available' and MatchDegree(network.node[i],task)>=1:
            return i
    return 'notfound'


# 项目执行过程中，继续找匹配度大于等于1的个体
def addMember(task,network):

    team = searchTeam(task[0])
    for m in team['members']:
        for node in network.neighbors(m):
            if network.node[node]['status']=='available'and MatchDegree(network.node[node],task) and task[0] == max_payoff(node,network):
                ToBusy(node,network.node[node],task[0])
                team['members'].append(node)
                update_team_list(team)
                return

#更新团队信息
def update_team_list(team):
    for li in TeamList:
        if li['task']==team['task']:
            members = team['members']
            li.update({'members':members})
            return

#根据项目ID找团队
def searchTeam(taskId):
    for team in TeamList:
        if team['task'] == taskId:
            return team

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
    for mem in team['members']:
        if network.node[mem]['skill'][i]>max and network.node[mem]['status'] == 'occupied':
            max = network.node[mem]['skill'][i]
    if max == 0:
        return 'notfound'
    else:
        temp = []
        for member in team['members']:
            if network.node[member]['skill'][i] == max and network.node[member]['status'] == 'occupied':
                temp.append(member)

        return random.SystemRandom().sample(temp,1)[0]
# 返回team中等待分派任务的成员数量
def memberWaiting(network,team):
    i = 0
    for j in team['members']:
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

def process():

    print '============================================================='
    print '============= start the simulation of CI ===================='
    print '============================================================='
    print 'initializing......'
    print

    #生成网络拓扑
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

    #初始化开发者的知识
    PersonSkill = chushihua.GenSkillForPerson(PersonNum)
    #初始化开发项目的知识需求
    ProjectsSkill = chushihua.GenSkillForProject(ProjectNum)
    #初始化项目
    ProjectsList= chushihua.init_project(ProjectsSkill)
    #初始化群集
    G = chushihua.init_person(G,PersonSkill)

    count=0
    global day
    day = 0

    while 1:
        completionNum = completion(ProjectsList)

        rate = completionNum/float(ProjectNum)*100
        print '============================================================='
        print 'day%s      %s个人     %s个项目完成了%s个,完成百分之%s            '%(day,PersonNum,ProjectNum,completionNum,rate)
        print '============================================================='
        rateline = '%s,%s,%s,%s,%s,%s,%s'%(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),type,ProjectNum,PersonNum,everageDegree,day,rate)
        ratefile.write(rateline+'\n')
        day +=1

        #==========================团队动态组建=======================
        for num,project in enumerate(ProjectsList):
            if project[1]['status'] == 'undone':
                #给项目第一次匹配开发者
                AssignTask(ProjectsList[num],G)
                ProjectsList[num][1]['start'] = day
            if project[1]['status'] == 'processing':
                #在任务未完成时，接下来的每一个天可以给团队增加一个成员
                addMember(ProjectsList[num],G)
        # ==========================团队动态组建=======================

        #待移除团队列表
        rmlist = []

        # 团队作业
        for team in TeamList:
             if ProjectsList[team['task']][1]['workload']>0:
                 total_rate = 0
                 for member in team['members']:
                     total_rate = total_rate + G.node[member]['rate']

                 ProjectsList[team['task']][1]['workload'] = ProjectsList[team['task']][1]['workload'] - total_rate
             else:
                 rmlist.append(team)


        #结算已完成项目的成本
        for dtsk in rmlist:
            count+=1
            TeamList.remove(dtsk)
            tms=dtsk['members']
            for tm in tms:
                G.node[tm]['end'] = day
                G.node[tm]['status'] = 'available'
            ProjectsList[dtsk['task']][1]['end']=day
            ProjectsList[dtsk['task']][1]['time']=ProjectsList[dtsk['task']][1]['end']-ProjectsList[dtsk['task']][1]['start']
            ProjectsList[dtsk['task']][1]['status']='done'
            print 'task %s is done!!!'%(dtsk['task'])
            print 'it costs %s people %s days'%(len(tms),ProjectsList[dtsk['task']][1]['time'])
            if switchbutton == 1:
                print  ProjectsList[dtsk['task']]
            print
        #结算平均成本
        if len(TeamList)==0:
            completionNum = completion(ProjectsList)
            rate = completionNum/float(ProjectNum)*100
            print '============================================================='
            print '现在处于 %s 网络 ,有 %s 个节点,网络平均度为 %s'%(conf.items('Graph')[0][1],NodeNum,everageDegree)

            print 'day%s      %s个人     %s个项目完成了%s个,完成百分之%s            '%(day,PersonNum,ProjectNum,completionNum,rate)
            print '========== end the simulation and show the results ==========='
            rateline = '%s,%s,%s,%s,%s,%s,%s'%(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),type,ProjectNum,PersonNum,everageDegree,day,rate)
            ratefile.write(rateline+'\n')
            total_time=0
            for i in ProjectsList:
                total_time+=i[1]['time']
            if count==len(ProjectsList):
                print 'all tasks are done!!!!! '
                print 'it takes %s days in average'%(float(total_time)/float(count))
            else:
                print '%s of %s tasks is done,the rest of tasks cannot find a match.'%(count,len(ProjectsList))
                print 'it takes %s days in totol'%(day)
                print 'it takes %s days in average'%(float(total_time)/float(count))

            line='%s,%s,%s,%s,%s,%s,%s'%(type,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),len(G.node),everageDegree,len(ProjectsList),day,float(total_time)/float(count))
            csvfile.write(line+'\n')

            break

def expriment(data):
    numOfExpri = 0
    number = data[0][1]
    for num in range(int(number)):
        process()
        numOfExpri +=1
    return numOfExpri



if __name__=='__main__':
    conf = ConfigParser.ConfigParser()
    conf.read('conf.cfg')

    rate = '../results/' + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + '_rate.csv'
    ratefile = open(rate, 'a')
    records = '../results/' + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + '_node.csv'
    csvfile = open(records, 'a')

    typeList = ['er','ws','ba','regular']
    for type in typeList:
        PersonNum = int(conf.items('Person')[0][1])
        ProjectNum = int(conf.items('Task')[0][1])
        p = 0.004
        m_ws = 4
        m_ba = 2
        m_re = 4

        # 考察网络结构对于完成率的影响
        # NodeNum = PersonNum
        # numdo = expriment(conf.items('Expriment'))
        # print('expriment has run %s times in all'%(numdo))

        #考察节点数的影响
        m_ws = 16
        m_ba = 8
        m_re = 16
        for i in range(50):
            PersonNum += 20
            p = round(16,5)/round(PersonNum,5)
            NodeNum = PersonNum
            # numdo为反复实验的次数
            numdo = expriment(conf.items('Expriment'))
            print('expriment has run %s times in all'%(numdo))


        #  考察平均度的影响
        # for j in range(50):
        #     p += 0.002
        #     m_ws += 2
        #     m_ba += 1
        #     m_re += 2
        #     NodeNum = PersonNum
        #     # numdo为反复实验的次数
        #     numdo = expriment(conf.items('Expriment'))
        #     print('expriment has run %s times in all'%(numdo))
        # csvfile.close()
        # ratefile.close()

