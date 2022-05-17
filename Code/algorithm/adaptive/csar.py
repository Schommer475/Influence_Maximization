# -*- coding: utf-8 -*-
"""
Created on Wed May 11 20:57:36 2022

@author: Tim Schommer
"""

from algorithm.algorithm import Algorithm
from application.application import Application
from parameters.parameterization_classes import ParamSet
from Utilities.program_vars import joint_index
import numpy as np
from scipy.linalg import hadamard

class CSAR(Algorithm):
    def __init__(self, params):
        self.params = params
        self.K = params.get("seed_set_size")
        self.T = params.get("time_horizon")
        
        
        self.error_prob = 1/self.T
        
    def run(self, app: Application, pset: ParamSet, timestamp:str, randId:str):
        N = pset.get(joint_index, "N")
        K = self.K
        T = self.T

        rewards = np.zeros(T)

        arm_indices = {item:index for index, item in enumerate(app.listOptions())}
        active_set = np.array(list(arm_indices.keys()))
        
        run_p = RunParams(rewards, active_set, app)

        mu_hat = np.zeros(N)

        r = 1
        Delta = 1/np.power(2, r)
        nr = int(np.power(2, 2*r+1)*np.log(N/self.error_prob))
        partitions = self.create_arm_partition(run_p)


        while (run_p.t < T):

            for partition in partitions:
                mu_hat[partition] = self.estimator(np.array(partition), nr,run_p)
                if(run_p.t >= T):
                    break

            if(run_p.t >= nr*2*self.K*len(partitions)):
                sorting = np.argsort(-mu_hat)
                print(run_p.t, nr, Delta, r, mu_hat)
                keep_mask = np.ones(len(run_p.active_set), dtype=bool)

                for arm_id, arm in enumerate(run_p.active_set):
                    if (mu_hat[arm_indices[arm]] > (mu_hat[sorting[K]] + 2*Delta)):
                        keep_mask[arm_id] = 0
                        run_p.accept_set += [arm]

                    if (mu_hat[arm] < (mu_hat[sorting[K-1]] - 2*Delta)):
                        keep_mask[arm_id] = 0
                        run_p.reject_set += [arm_indices[arm]]

                run_p.active_set = run_p.active_set[keep_mask]

                if(len(run_p.active_set) + len(run_p.accept_set) == K):
                    break

                r += 1
                Delta = 1/np.power(2, r)
                nr = int(np.power(2, 2*r+1)*np.log(N/self.error_prob))
                partitions = self.create_arm_partition(run_p)

        final_action = run_p.accept_set + run_p.active_set.tolist()    
        final_action = final_action[:K]

        print(final_action)
        while(run_p.t < T):
            run_p.rewards[self.t] = run_p.getReward(final_action)
            run_p.t += 1

        return {"best_seed_sets":final_action, "rewards":run_p.rewards}
        
    def refresh(self):
        ...
    
    def create_arm_partition(self, run_p):
        K = self.K
    
        num_partitions = np.ceil(len(run_p.active_set.tolist())/(2*K))
    
        partitions = []
        total_arms = run_p.accept_set + run_p.active_set.tolist()
    
        for i in range(int(num_partitions)):
            if(2*(i+1)*K <= len(total_arms)):
                partition = total_arms[2*i*K: 2*(i+1)*K]
            else:
                gap = 2*K - (len(total_arms) - 2*i*K)
                partition = total_arms[2*i*K:] + total_arms[-gap:]
            assert(len(partition) == 2*K)
            partitions.append(partition)
    
        return partitions
    
    def calc_reward_estimates(self, sample_mean, H):
        K = len(H)
        diff_vector = np.zeros(K)
        row = 0
        diff_vector[row] = sample_mean[row, 0] + sample_mean[row, 1]
        row += 1
        while row < K:
            diff_vector[row] = sample_mean[row, 1] - sample_mean[row, 0]
            row += 1
    
        theta_hat = np.dot(H.T, diff_vector)/2
    
        return theta_hat
    
    
    def estimator(self, partition, num_samples, run_p):
        K = int(len(partition)/2)
    
        H = hadamard(2*K)
        bool_H = (H == True)
    
        count = 0
    
        sample_mean = np.zeros([2*K, 2])
        sample_count = np.zeros([2*K, 2])
    
        max_count = num_samples*(2*K*2)
    
    
        while (count < max_count):
            row = 0
            for b in [0, 1]:
                action_set = np.zeros(2*K, dtype = bool)
                action_set[b*K:(b+1)*K] = True
                action = partition[action_set].tolist()
                reward_t = run_p.getReward(action)
    
                sample_mean[row, b] = reward_t + sample_count[row, b]*sample_mean[row, b]
                sample_count[row, b] += 1
                sample_mean[row, b] /= sample_count[row, b]
    
                run_p.rewards[run_p.t] = reward_t
                run_p.t += 1
                count += 1
    
                if (run_p.t >= self.T):
                    return self.calc_reward_estimates(sample_mean, H)
    
            row = 1
            while (row < len(bool_H)):
                for b, side in enumerate([True, False]):
                    action_set = side ^ bool_H[row]
                    action = partition[action_set].tolist()
    
    
                    reward_t = run_p.getReward(action)
    
                    sample_mean[row, b] = reward_t + sample_count[row, b]*sample_mean[row, b]
                    sample_count[row, b] += 1
                    sample_mean[row, b] /= sample_count[row, b]
    
                    run_p.rewards[run_p.t] = reward_t
                    run_p.t += 1
                    count += 1
    
                    if (run_p.t >= self.T):
                        return self.calc_reward_estimates(sample_mean, H)
    
                row += 1
    
        return self.calc_reward_estimates(sample_mean, H)
        
class RunParams:
    def __init__(self, rewards, active_set, app):
        self.accept_set = []
        self.reject_set = []
        self.active_set = active_set
        self.t = 0
        self.rewards = rewards
        
        self.app = app
        
    def getReward(self, choices):
        return self.app.getReward(choices)

def createInstance(params):
    return CSAR(params)