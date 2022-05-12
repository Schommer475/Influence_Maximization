# -*- coding: utf-8 -*-
"""
Created on Fri Apr  1 15:16:35 2022

@author: Tim Schommer
"""
from algorithm.algorithm import Algorithm
from application.application import Application
from parameterization.parameterization_classes import ParamSet
import numpy as np
import copy

class CMAB(Algorithm):
    def __init__(self, data):
        self.data = data
        self.K = data.get("seed_set_size")
        self.T = data.get("time_horizon")
        
        self.error_prob = 1 / data.get("error_prob")
        
        
        
    def run(self, app: Application, pset: ParamSet, timestamp:str, randId:str):
        N = app.getOptionCount()
        precision = np.power(((N*np.log(2*N*self.T*self.error_prob))/self.T), 1/3)
        groups = self.generate_groups(app, N)
        t = 0
        reward_t = np.zeros(self.T)
        
        num_groups = int(np.ceil(N/(self.K+1)))
        sorted_groups = np.zeros([num_groups, self.K], dtype = int)
        
        run_p = RunParams(N, precision, groups, reward_t, sorted_groups, app)
        
        for group in range(num_groups):
            run_p.sorted_groups[group] = self.sort_group(group, run_p)

        opt_arms = sorted_groups[0]

        for group in range(1,num_groups):
            if run_p.t < self.T:
                opt_arms = self.merge_groups(opt_arms, group, run_p)
            else:
                pass
                
        while( t < self.T ):
            reward_t[t] = run_p.getReward(opt_arms)
            t += 1
                
        return {"best_seed_sets":run_p.best_seed_sets, "rewards":reward_t}
        
    def generate_groups(self, app, N):
        num_groups = int(np.ceil(N/(self.K+1)))

        groups = np.zeros([num_groups, self.K+1], dtype = int)
        arms = copy.copy(app.listOptions())
        np.random.shuffle(arms)

        for i in range(num_groups):
            for j in range(self.K + 1):
                groups[i, j] = arms[int((i*(self.K + 1) + j)%N)]
                
        return groups
    
    def get_round_params(self, r, N):
        delta_r = np.power(2.0, -r)
        n_r = np.log(2*N*self.T*self.error_prob)*np.power(2, 2*r)

        return delta_r, n_r
    
    def sort_group(self, group_id, run_p):
        r = 1
        delta_r, n_r = self.get_round_params(r, run_p.N)

        n_G = np.zeros(self.K + 1)
        mu_hat_G = np.zeros(self.K + 1)
        UCB = mu_hat_G + delta_r
        LCB = mu_hat_G - delta_r

        sort_id = np.argsort(UCB)[::-1]

        sorted_arms = []

        while((run_p.t < self.T) and (len(sorted_arms) == 0)):

            for arm_index in range(self.K + 1):
                if(arm_index not in sorted_arms):
                    action = run_p.groups[group_id, :arm_index].tolist() + run_p.groups[group_id, arm_index+1:].tolist()

                reward = run_p.getReward(action)

                run_p.reward_t[run_p.t] = reward
                run_p.t += 1

                mu_hat_G[arm_index] = n_G[arm_index]*mu_hat_G[arm_index] + reward
                n_G[arm_index] += 1
                mu_hat_G[arm_index] /= n_G[arm_index]

                if(run_p.t >= self.T):
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
                delta_r, n_r = self.get_round_params(r, run_p.N)
                if(delta_r < run_p.precision):
                    break

        UCB = mu_hat_G + delta_r
        sort_id = np.argsort(UCB)

        sorted_arms = run_p.groups[group_id, sort_id[:self.K]]
        return sorted_arms
    
    def merge_groups(self, opt_arm_group, group_id, run_p):
        to_merge_group = []
        for arm_id in run_p.sorted_groups[group_id, :]:
            if arm_id not in opt_arm_group:
                to_merge_group = to_merge_group + [arm_id]
                
        new_opt_arms = []
        placed_arms = 0

        r_opt = 1
        delta_opt, n_r_opt = self.get_round_params(r_opt, run_p.N)
        mu_hat_opt = 0
        n_opt = 0
        
        opt_group_itr = 0
        exc_group_itr = 0
        
        reset_round = True
        if(reset_round):
            r_exc = 1
            delta_exc, n_r_exc = self.get_round_params(r_exc, run_p.N)
            mu_hat_exc = 0
            n_exc = 0
            reset_round = False

        exc_group = np.copy(opt_arm_group)
        exc_group[opt_group_itr] = to_merge_group[exc_group_itr] 

        while((placed_arms < self.K) and (run_p.t < self.T)):
            if((n_opt < n_r_opt) and (run_p.t < self.T)):
                reward = run_p.getReward(opt_arm_group)
                run_p.reward_t[run_p.t] = reward
                run_p.t += 1

                mu_hat_opt = n_opt*mu_hat_opt + reward
                n_opt += 1
                mu_hat_opt /= n_opt

            if((n_exc < n_r_exc) and (run_p.t < self.T)):
                reward = run_p.getReward(exc_group)
                run_p.reward_t[run_p.t] = reward
                run_p.t += 1

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

            elif ( (delta_exc < run_p.precision) and 
                   (delta_opt < run_p.precision) ):
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
                delta_exc, n_r_exc = self.get_round_params(r_exc, run_p.N)
                mu_hat_exc = 0
                n_exc = 0
                reset_round = False
                
                exc_group = np.copy(opt_arm_group)
                exc_group[opt_group_itr] = to_merge_group[exc_group_itr] 

            if( (n_exc > n_r_exc) and
                (delta_exc > run_p.precision) ):
                r_exc += 1
                delta_exc, n_r_exc = self.get_round_params(r_exc, run_p.N)

            if( (n_opt > n_r_opt) and
                (delta_opt > run_p.precision) ):
                r_opt += 1
                delta_opt, n_r_opt = self.get_round_params(r_opt, run_p.N)


        return new_opt_arms
        
    def refresh(self):
        ...

class RunParams:
    def __init__(self, N, precision, groups, reward_t, sorted_groups, app):
        self.N = N
        self.precision = precision
        self.groups = groups
        self.t = 0
        self.reward_t = reward_t
        
        self.sorted_groups = sorted_groups
        self.app = app
        self.best_seed_sets = []
        
    def getReward(self, choices):
        self.best_seed_sets.append(list(np.array(choices)))
        return self.app.getReward(choices)

def createInstance(params):
    return CMAB(params)