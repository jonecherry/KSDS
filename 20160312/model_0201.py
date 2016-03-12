'''
Created on 2015-12-06

'''

import networkx as nx
from networkx import utils
import ConfigParser
#import matplotlib.pyplot as plt
import random
import math
import time
import csv



TeamList=[]
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

def GenSkill(data):
#    return Return n lists of sequence from a power law distribution.
    n=int(data[0][1])
    exponent=float(data[1][1])
#     numlist=[]
    numlist=utils.powerlaw_sequence(n,exponent)
    numlist.sort(reverse=True)

    for i,num in enumerate(numlist):

        if num<int(num)+0.5:
            numlist[i]=int(num)
        elif num>=int(num)+0.5:
            numlist[i]=int(num)+1
    print "1-----------------------------"
    print numlist
    max=numlist[0]
    all=range(max)
#    print all
    for j,num1 in enumerate(numlist):
        a=random.SystemRandom()
#         print a
        numlist[j]=a.sample(all,num1)
    print " 2---------------------------"
    print numlist
    return numlist

def GenSkillForPerson(data):
    skilllist = []
    for i in range(data[0][1]):
        for j in range(10):
            skill = random.random()
            if skill < int(skill)+0.5:
                skill = int(skill)
            elif skill >= int(skill)+0.5:
                skill = int(skill)+1
            num[j] = skill

        skilllist[i] = num
    return skilllist


def ToBusy(person,tasknum):
    person['status']='occupied'
    person['task'].append(tasknum)

#def ToFree(Team):
#    for mb in Team:


def AssignTask(task,network):
    Team={'member':[]}

    for i in network.node:

#task:[j,{'skill':skill,'workload':len(skill)*BasicLoad,'limit':int(math.sqrt(len(skill))+2),'money':0,'time':0,'status':'undone','start':0,'end':0}]
#node:{0: {'salary': 15811.388300841898, 'status': 'available', 'skill': [4, 1, 8, 0, 9, 6, 7, 5, 2, 3], 'task': []}}
#when task skill requirement is smaller than employee&status is available,then assign it to this employee
        if set(task[1]['skill'])<=set(network.node[i]['skill']) and network.node[i]['status']=='available':
            #configure employee
            ToBusy(network.node[i],task[0])
            #configure task
            task[1]['status']='in progress'
            print '%s is assigned to task %s as leader'%(i,task[0])
            Team['task']=task[0]
            Team['leader']=i
            for j in network.neighbors(i):
                #when empoyee and task have the same skills assign him to this task
                if len(set(network.node[j]['skill'])&set(task[1]['skill']))>0 and network.node[j]['status']=='available' and len(Team['member'])<=task[1]['limit']:
                    ToBusy(network.node[j],task[0])
                    print '%s is assigned to task %s'%(j,task[0])
                    Team['member'].append(j)
            TeamList.append(Team)
            break





if __name__=='__main__':
    # -*- coding: UTF-8 -*-
    print '============================================================='
    print '============= start the simulation of CI ===================='
    print '============================================================='
#    time.sleep(1)
    print 'initializing......'
#    time.sleep(2)
    conf=ConfigParser.ConfigParser()
    conf.read('conf.cfg')
    G=CreateGraph(conf.items('Graph'))
    #initial people skills
    PersonSkill=GenSkillForPerson(conf.items('Person'))
    #initial task skill requirement
    TaskSkill=GenSkill(conf.items('Task'))
    BasicSalary=int(conf.items('Person')[2][1])
    BasicLoad=int(conf.items('Task')[2][1])

    TaskList=[]
    #=======================================================================
    # initialize the environment
    #=======================================================================
    #tasks
    for j,skill in enumerate(TaskSkill):
        temp=[j,{'skill':skill,'workload':len(skill)*BasicLoad,'limit':int(math.sqrt(len(skill))+2),'money':0,'time':0,'status':'undone','start':0,'end':0}]
        TaskList.append(temp)
    print TaskList

    #employee
    for i,node in enumerate(G.node):
        G.node[i]['skill']= PersonSkill[i]
        G.node[i]['salary']=math.sqrt(len(PersonSkill[i]))*BasicSalary
        G.node[i]['task']=[]
        G.node[i]['status']='available'

    print G.node

    #=======================================================================
    # assign and process tasks
    #=======================================================================
    day=0
    count=0
    while 1:

#        time.sleep(1)
        day+=1
        print '============================================================='
        print '                          day%s                              '%(day)
        print '============================================================='
        for num,task in enumerate(TaskList):
            if task[1]['status']=='undone':
                AssignTask(TaskList[num],G)
                TaskList[num][1]['start']=day

            else :
                pass
        rmlist=[]
        print TeamList

        #team:{'member': [2, 48, 49, 26], 'task': 0, 'leader': 0}, {'member': [24], 'task': 2, 'leader': 1}
        for team in TeamList:
            if TaskList[team['task']][1]['workload']<=0:
                rmlist.append(team)
            teamspeed=(len(team['member'])+1)
            TaskList[team['task']][1]['workload']-=teamspeed
        print 'rmlist:----------'
        print rmlist

        for dtsk in rmlist:
            count+=1
            TeamList.remove(dtsk)
            teamcost=0
            tms=dtsk['member']
            tms.append(dtsk['leader'])
            for p in tms:
                G.node[p]['status']='available'
                teamcost+=G.node[p]['salary']
#                print teamcost
            TaskList[dtsk['task']][1]['end']=day
            TaskList[dtsk['task']][1]['time']=TaskList[dtsk['task']][1]['end']-TaskList[dtsk['task']][1]['start']
            TaskList[dtsk['task']][1]['money']=teamcost*(float(TaskList[dtsk['task']][1]['time'])/30.0)
            TaskList[dtsk['task']][1]['status']='done'
            print 'task %s is done!!!'%(dtsk['task'])
            print 'it costs %s people %s days and %s rmb'%(len(tms),TaskList[dtsk['task']][1]['time'],TaskList[dtsk['task']][1]['money'])
#        print G.node
#        print TaskList
#        print TeamList

        if len(TeamList)==0:
            print '========================================================================'
            print '============= end the simulation and show the results =================='
            print '========================================================================'
            print TeamList
            total_time=0
            total_money=0
            for i in TaskList:
                total_money+=i[1]['money']
                total_time+=i[1]['time']
            if count==len(TaskList):
                print 'the projecet is done!!!!! '
                print 'it takes %s days and %s rmb in totol'%(day,total_money)
                print 'it takes %s days and %s rmb in average'%(float(total_time)/float(count),total_money/float(count))
            else:
                print '%s of %s tasks is done,the rest of tasks cannot find a match.'%(count,len(TaskList))
                print 'it takes %s days and %s rmb in totol'%(day,total_money)
                print 'it takes %s days and %s rmb in average'%(float(total_time)/float(count),total_money/float(count))
            csvfile=open('result.csv','a')
            line='%s,%s,%s,%s,%s,%s,%s,%s'%(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),len(G.node),len(TaskList),count,day,total_money,float(total_time)/float(count),total_money/float(count))
            csvfile.write(line+'\n')
            csvfile.close()
            break
