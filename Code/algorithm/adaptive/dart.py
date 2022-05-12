# -*- coding: utf-8 -*-
"""
Created on Thu May 12 10:14:16 2022

@author: Tim Schommer
"""

from algorithm.algorithm import Algorithm
from application.application import Application
from parameterization.parameterization_classes import ParamSet
import numpy as np
import copy

class DART(Algorithm):
    def __init__(self, params):
        self.params = params
        self.K = params.get("seed_set_size")
        self.T = params.get("time_horizon")
        
    def run(self, app: Application, pset: ParamSet, timestamp:str, randId:str):
        N = app.getOptionCount()
        error_prob = 1/(N*self.K*self.T)
        precision = np.sqrt((N*np.log(N*self.T))/(self.T*self.K))
        
        t = 0
        A = []
        current_confused_arms = np.array(copy.copy(app.listOptions()))
        R = []
        run_p = RunParams(app)
        
        reward_list = []
        
        K = self.K
        T = self.T

        print(N, K)
        
        r = 1
        
        Delta, nr = self.__update_round_params__(r, N)
        
        num_plays = np.zeros(N)
        mu = np.zeros(N)
        
        num_arms = len(current_confused_arms)
        while(t < T):
    
            new_K = K-len(A)
            factor = (num_arms - new_K)/(num_arms-1)
            
            if( (num_arms + len(A) == 0) or
                (T - t < np.ceil(num_arms/(K-len(A)))) ):
                print("breaking here after no arms left to explore")
                print(A)
                print(current_confused_arms)
                print(R)
                print(T, t, np.ceil(num_arms/(K-len(A))))
                print(r, Delta, nr)
                break
                
                
            np.random.shuffle(current_confused_arms)
#             print(current_confused_arms)
#             print(mu)
            
            for i in range(int(np.ceil(num_arms/(K-len(A))))):
                action = []
                action += A

                if ((i+1)*(K-len(A)) <= num_arms):
                    action += current_confused_arms[i*(K-len(A)):(i+1)*(K-len(A))].tolist()
                else:
                    action += current_confused_arms[num_arms - (K-len(A)):num_arms].tolist()

                t += 1
                reward_t = self.__play_action__(action, run_p, t)
                reward_list.append(reward_t)
#                 print(t, action, reward_t)

#                 if ((i+1)*(K-len(A)) <= num_arms):
#                     current_list = action
#                 else:
#                     current_list = action[i*(K-len(A)): num_arms]

                num_plays[action] += 1
                mu[action] = ((num_plays[action]-1)*mu[action]+(reward_t/factor))/num_plays[action]                

            sorted_index = np.argsort(-mu)
            last_K = mu[sorted_index[K-1]]
            top_K_1 = mu[sorted_index[K]]
            
            next_round_arms = np.ones(num_arms, dtype = bool)
            
            if(num_arms-new_K == 0):
                print(num_arms, K, len(A))
            
            threshold = 2*Delta
#             threshold = 2*((self.N - self.K)/(self.N-1))*Delta
#             threshold = 2*Delta
            
            give_space = False
            for i in range(num_arms):
                if(mu[current_confused_arms[i]] - top_K_1 > threshold):
                    A.append(current_confused_arms[i])
                    next_round_arms[i] = False

                    print(sorted_index, sorted_index[K])
                    print(top_K_1, threshold)
                    print(mu[current_confused_arms[i]], num_plays[current_confused_arms[i]])

                    print("accepted arms", threshold, A)
                    give_space = True
                elif (last_K - mu[current_confused_arms[i]] > threshold):
                    R.append(current_confused_arms[i])
                    next_round_arms[i] = False
                    
                    print(sorted_index, sorted_index[K-1])
                    print(last_K, threshold)
                    print(mu[current_confused_arms[i]], num_plays[current_confused_arms[i]])
                    print("rejected arms", threshold, R)
                    give_space = True

            current_confused_arms = current_confused_arms[next_round_arms] 
            num_arms = len(current_confused_arms)
                    
            if(give_space):
                print(mu)
                print(num_plays, np.sum(num_plays), t)
                print("current confused arms: ", current_confused_arms)
                print("\n")
                                
            assert(len(A) <= K)
            if( (len(A) + num_arms == K) or
                (len(A) == K) ):
                print(mu)
                print(r, Delta, nr)
                print(A)
                print("breaking here after fill top K positions at time: ", t)
                break
                        
            if( t > nr*np.ceil(num_arms/(K-len(A))) ):
#                     print(A)
#                     print(mu)

                r += 1
                Delta, nr = self.__update_round_params__(r, N)
    
                if(Delta < precision):
                    print("Delta got too low, breaking")
                    print(Delta, precision, t, precision)
                    break
                
        #select top K arms after exiting
        action = A + current_confused_arms[np.argsort(-mu[current_confused_arms])[0:K-len(A)]].tolist()
        
        while (t < T):
            t+=1
            reward_t = self.__play_action__(action, run_p, t)
            reward_list.append(reward_t)
            
            
        print(mu)
        print(num_plays)
        return {"best_seed_sets":run_p.best_seed_sets, "rewards":reward_list}
        
    def refresh(self):
        ...
        
    def __update_round_params__(self, r, N):
        delta = 1/np.power(2, r)
        nr = int(np.power(2, 2*r)*np.log(N*self.T))
        
        print(r, delta, nr)
        
        return delta, nr
    
    def __play_action__(self, action, t = 0):
        reward = self.environment.reward(action)
        if(t % (self.T/100) == 0):
            print(f"Finished {100*t / (self.T)}% of runs, current run {t}")
        return reward
    
class RunParams:
    def __init__(self, app):
        self.app = app
        self.best_seed_sets = []
        
    def getReward(self, choices):
        self.best_seed_sets.append(list(np.array(choices)))
        return self.app.getReward(choices)

def createInstance(params):
    return DART(params)