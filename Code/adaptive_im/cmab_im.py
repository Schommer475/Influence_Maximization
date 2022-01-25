
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 18 02:23:56 2019

@author: abhishek.umrawal
"""

"Importing necessary modules"
from Utilities.influence import influence
import numpy as np
import os as os; os.getcwd()
import random

def cmab_im(network, seed_set_size, diffusion_model, num_times):

    np.random.seed(int(random.uniform(0, 1000000)))
    
    "Defining CMAB class"
    class CMAB:
        def __init__(self, N, K, T, env, error_prob=1):
            self.N = N
            self.K = K
            self.T = T

            self.env = env

            self.error_prob = 1/error_prob
            self.precision = np.power(((self.N*np.log(2*self.N*self.T*self.error_prob))/self.T), 1/3)

            self.generate_groups()

            self.t = 0
            self.reward_t = np.zeros(self.T)

        def generate_groups(self):
            num_groups = int(np.ceil(self.N/(self.K+1)))

            self.groups = np.zeros([num_groups, self.K+1], dtype = int)
            arms = np.arange(self.N)
            np.random.shuffle(arms)

            for i in range(num_groups):
                for j in range(self.K + 1):
                    self.groups[i, j] = arms[int((i*(self.K + 1) + j)%self.N)]

        def get_round_params(self, r):
            delta_r = np.power(2.0, -r)
            n_r = np.log(2*self.N*self.T*self.error_prob)*np.power(2, 2*r)

            return delta_r, n_r


        def sort_group(self, group_id):
            r = 1
            delta_r, n_r = self.get_round_params(r)

            n_G = np.zeros(self.K + 1)
            mu_hat_G = np.zeros(self.K + 1)
            UCB = mu_hat_G + delta_r
            LCB = mu_hat_G - delta_r

            sort_id = np.argsort(UCB)[::-1]

            sorted_arms = []

            while((self.t < self.T) and (len(sorted_arms) == 0)):

                for arm_index in range(self.K + 1):
                    if(arm_index not in sorted_arms):
                        action = self.groups[group_id, :arm_index].tolist() + self.groups[group_id, arm_index+1:].tolist()

                    reward = self.env.reward(action)

                    self.reward_t[self.t] = reward
                    self.t += 1

                    mu_hat_G[arm_index] = n_G[arm_index]*mu_hat_G[arm_index] + reward
                    n_G[arm_index] += 1
                    mu_hat_G[arm_index] /= n_G[arm_index]

                    if(self.t >= self.T):
                        break

                UCB = mu_hat_G + delta_r
                LCB = mu_hat_G - delta_r
                sort_id = np.argsort(UCB)[::-1]

                if( (sort_id[0] not in sorted_arms) and \
                    (LCB[sort_id[0]] > UCB[sort_id[1]])):
                    sorted_arms = sorted_arms + [sort_id[0]]

                for arm_id in range(1,self.K):
                    if( (sort_id[arm_id] not in sorted_arms) and \
                        (LCB[sort_id[arm_id]] > UCB[sort_id[arm_id+1]]) and \
                        (UCB[sort_id[arm_id]] < LCB[sort_id[arm_id-1]])):   
                        sorted_arms = sorted_arms + [sort_id[arm_id]]

                if( (sort_id[self.K] not in sorted_arms) and \
                    (UCB[sort_id[self.K]] < LCB[sort_id[self.K-1]])):
                    sorted_arms = sorted_arms + [sort_id[self.K]]

                if (len(sorted_arms) == (self.K + 1)):
                    break

                if(np.max(n_G) > n_r):
                    r += 1
                    delta_r, n_r = self.get_round_params(r)
                    if(delta_r < self.precision):
                        break

            UCB = mu_hat_G + delta_r
            sort_id = np.argsort(UCB)

            sorted_arms = self.groups[group_id, sort_id[:self.K]]
            return sorted_arms

        def merge_groups(self, opt_arm_group, group_id):
            to_merge_group = []
            for arm_id in self.sorted_groups[group_id, :]:
                if arm_id not in opt_arm_group:
                    to_merge_group = to_merge_group + [arm_id]
                    
            new_opt_arms = []
            placed_arms = 0

            r_opt = 1
            delta_opt, n_r_opt = self.get_round_params(r_opt)
            mu_hat_opt = 0
            n_opt = 0
            
            opt_group_itr = 0
            exc_group_itr = 0
            
            reset_round = True
            if(reset_round):
                r_exc = 1
                delta_exc, n_r_exc = self.get_round_params(r_exc)
                mu_hat_exc = 0
                n_exc = 0
                reset_round = False

            exc_group = np.copy(opt_arm_group)
            exc_group[opt_group_itr] = to_merge_group[exc_group_itr] 

            while((placed_arms < self.K) and (self.t < self.T)):
                if((n_opt < n_r_opt) and (self.t < self.T)):
                    reward = self.env.reward(opt_arm_group)
                    self.reward_t[self.t] = reward
                    self.t += 1

                    mu_hat_opt = n_opt*mu_hat_opt + reward
                    n_opt += 1
                    mu_hat_opt /= n_opt

                if((n_exc < n_r_exc) and (self.t < self.T)):
                    reward = self.env.reward(exc_group)
                    self.reward_t[self.t] = reward
                    self.t += 1

                    mu_hat_exc = n_exc*mu_hat_exc + reward
                    n_exc += 1
                    mu_hat_exc /= n_exc

                UCB_opt = mu_hat_opt + delta_opt
                LCB_opt = mu_hat_opt - delta_opt

                UCB_exc = mu_hat_exc + delta_exc
                LCB_exc = mu_hat_exc - delta_exc

                if ( LCB_exc > UCB_opt ):
                    new_opt_arms = new_opt_arms + [to_merge_group[exc_group_itr]]
                    exc_group_itr += 1
                    placed_arms += 1
                    reset_round = True

                elif ( LCB_opt > UCB_exc ):
                    new_opt_arms = new_opt_arms + [opt_arm_group[opt_group_itr]]
                    opt_group_itr += 1
                    placed_arms += 1
                    reset_round = True

                elif ( (delta_exc < self.precision) and 
                       (delta_opt < self.precision) ):
                    if(UCB_exc > UCB_opt):
                        new_opt_arms = new_opt_arms + [to_merge_group[exc_group_itr]]
                        exc_group_itr += 1
                    else:
                        new_opt_arms = new_opt_arms + [opt_arm_group[opt_group_itr]]
                        opt_group_itr += 1

                    placed_arms += 1
                    reset_round = True

                if(exc_group_itr >= len(to_merge_group)):
                    while(placed_arms < self.K):
                        new_opt_arms = new_opt_arms + [opt_arm_group[opt_group_itr]]
                        opt_group_itr += 1
                        placed_arms += 1

                    break
                
                if(opt_group_itr >= self.K):
                    break

                if(reset_round):
                    r_exc = 1
                    delta_exc, n_r_exc = self.get_round_params(r_exc)
                    mu_hat_exc = 0
                    n_exc = 0
                    reset_round = False
                    
                    exc_group = np.copy(opt_arm_group)
                    exc_group[opt_group_itr] = to_merge_group[exc_group_itr] 

                if( (n_exc > n_r_exc) and
                    (delta_exc > self.precision) ):
                    r_exc += 1
                    delta_exc, n_r_exc = self.get_round_params(r_exc)

                if( (n_opt > n_r_opt) and
                    (delta_opt > self.precision) ):
                    r_opt += 1
                    delta_opt, n_r_opt = self.get_round_params(r_opt)


            return new_opt_arms


        def play_actions(self):
            num_groups = int(np.ceil(self.N/(self.K+1)))
            self.sorted_groups = np.zeros([num_groups, self.K], dtype = int)
            
            for group in range(num_groups):
                self.sorted_groups[group] = self.sort_group(group)

            #print(self.sorted_groups)
            opt_arms = self.sorted_groups[0]

            for group in range(1,num_groups):
                #print(opt_arms, self.sorted_groups[group])
                if self.t < self.T:
                    opt_arms = self.merge_groups(opt_arms, group)
                else:
                    pass
                    #print("Time horizon is insufficient!")
                    
            print("Finished searching for optimal arms, opt_action: ", opt_arms)
            print("Consumed time: ", self.t)
            while( self.t < self.T ):
                self.reward_t[self.t] = self.env.reward(opt_arms)
                self.t += 1
            print("Observed reward of optimal arm: ", self.N* np.mean(self.reward_t[self.t-100:]))                
            return self.reward_t, opt_arms

    "Defining MAB environment"
    class MAB_environment:
        def __init__(self, N, K):
            self.N = N
            self.K = K

        "reward/influence functions"
        def reward(self, arms_list):
            arm_reward = influence(network, list(np.array(arms_list)+1), diffusion_model, spontaneous_prob=[])/self.N
            best_seed_sets_cmab.append(list(np.array(arms_list)+1))
            return arm_reward

    "Performing CMAB"
    N = len(network.nodes)
    K = seed_set_size
    T = num_times
    best_seed_sets_cmab = []
    env = MAB_environment(N, K)
    agent = CMAB(N, K, T, env)
    obs_influences_cmab, _ = agent.play_actions()

    return best_seed_sets_cmab, list(np.array(obs_influences_cmab)*len(network.nodes))
