#! /usr/bin/python
# coding=utf-8
import csv
import os

import tensorflow as tf
import numpy as np

import BagOfEntailments

DIR = '../samples'


class Config(object):
    def __init__(self):
        self.L1_flag = True
        self.batch_size = 500
        self.train_times = 2
        self.margin = 1.0
        self.express_num = len(BagOfEntailments.Exps)


class WBOEModel(object):
    def __init__(self, config):
        margin = config.margin

        self.pos_h = tf.placeholder(tf.float32, [None, config.express_num])
        self.pos_t = tf.placeholder(tf.float32, [None, config.express_num])

        self.neg_h = tf.placeholder(tf.float32, [None, config.express_num])
        self.neg_t = tf.placeholder(tf.float32, [None, config.express_num])

        with tf.name_scope("embedding"):
            self.ont_embeddings = tf.get_variable(name="ont_embedding", shape=[1, config.express_num],
                                                  initializer=tf.contrib.layers.xavier_initializer(uniform=False))

            pos_h_e = self.pos_h * self.ont_embeddings
            pos_t_e = self.pos_t * self.ont_embeddings
            neg_h_e = self.neg_h * self.ont_embeddings
            neg_t_e = self.neg_t * self.ont_embeddings

        if config.L1_flag:
            pos = tf.reduce_sum(abs(pos_h_e - pos_t_e), 1, keep_dims=True)
            neg = tf.reduce_sum(abs(neg_h_e - neg_t_e), 1, keep_dims=True)
        else:
            pos = tf.reduce_sum((pos_h_e - pos_t_e) ** 2, 1, keep_dims=True)
            neg = tf.reduce_sum((neg_h_e - neg_t_e) ** 2, 1, keep_dims=True)

        with tf.name_scope("output"):
            self.loss = tf.reduce_sum(tf.maximum(pos - neg + margin, 0))


class Ontology(object):
    def __init__(self, batch_size, s_type):
        heads_pos, tails_pos = self.readHeadTail(os.path.join(DIR, s_type + '_Pairs_Pos.csv'))
        heads_neg, tails_neg = self.readHeadTail(os.path.join(DIR, s_type + '_Pairs_Neg.csv'))

        if s_type == 'BJ-HZ':
            kg_boe_bj = self.readBOE(os.path.join(DIR, 'BJ_BOE.csv'))
            kg_boe_hz = self.readBOE(os.path.join(DIR, 'HZ_BOE.csv'))
            h_boes_pos, t_boes_pos = self.KG2BOE(head_kgs=heads_pos, tail_kgs=tails_pos, head_boes=kg_boe_bj,
                                                 tail_boes=kg_boe_hz)
            h_boes_neg, t_boes_neg = self.KG2BOE(head_kgs=heads_neg, tail_kgs=tails_neg, head_boes=kg_boe_bj,
                                                 tail_boes=kg_boe_hz)
        else:
            kg_boe = self.readBOE(os.path.join(DIR, s_type + '_BOE.csv'))
            h_boes_pos, t_boes_pos = self.KG2BOE(head_kgs=heads_pos, tail_kgs=tails_pos, head_boes=kg_boe,
                                                 tail_boes=kg_boe)
            h_boes_neg, t_boes_neg = self.KG2BOE(head_kgs=heads_neg, tail_kgs=tails_neg, head_boes=kg_boe,
                                                 tail_boes=kg_boe)

        self.ph = np.array(h_boes_pos, dtype=np.float32)
        self.pt = np.array(t_boes_pos, dtype=np.float32)
        self.nh = np.array(h_boes_neg, dtype=np.float32)
        self.nt = np.array(t_boes_neg, dtype=np.float32)

        self.sample_size = len(h_boes_pos) if len(h_boes_pos) <= len(h_boes_neg) else len(h_boes_neg)
        self.batch_size = batch_size
        self.batch_num = self.sample_size / batch_size

        print 'sample_size: %d, batch_size: %d, batch_num: %d' % (self.sample_size, self.batch_size, self.batch_num)

    @staticmethod
    def KG2BOE(head_kgs, tail_kgs, head_boes, tail_boes):
        h_boes, t_boes = [], []
        for i in range(len(head_kgs)):
            h_kg = head_kgs[i]
            t_kg = tail_kgs[i]
            h_boe = head_boes[h_kg]
            t_boe = tail_boes[t_kg]
            if -1 not in h_boe and -1 not in t_boe:
                h_boes.append(h_boe)
                t_boes.append(t_boe)
        return h_boes, t_boes

    @staticmethod
    def readBOE(file_name):
        kb_boe = {}
        with open(file_name) as f:
            f_csv = csv.DictReader(f)
            for row in f_csv:
                KB = row['KB']
                boe = []
                for exp in BagOfEntailments.Exps:
                    boe.append(int(row[exp]))
                kb_boe[KB] = boe
        return kb_boe

    @staticmethod
    def readHeadTail(file_name):
        heads, tails = [], []
        with open(file_name) as f:
            f_csv = csv.DictReader(f)
            for row in f_csv:
                heads.append(row['head'])
                tails.append(row['tail'])
        return heads, tails

    def getBatch(self, b):
        bottom = b * self.batch_size
        top = (b + 1) * self.batch_size
        return self.ph[bottom:top], self.pt[bottom:top], self.nh[bottom:top], self.nt[bottom:top]


if __name__ == "__main__":
    s_type = 'BJ'
    #s_type = 'HZ'
    #s_type = 'BJ-HZ'

    config = Config()
    onto = Ontology(batch_size=config.batch_size, s_type=s_type)

    with tf.Graph().as_default():
        sess = tf.Session()
        initializer = tf.contrib.layers.xavier_initializer(uniform=False)
        with tf.variable_scope("model", reuse=None, initializer=initializer):
            model = WBOEModel(config=config)
        global_step = tf.Variable(0, name="global_step", trainable=False)
        optimizer = tf.train.GradientDescentOptimizer(0.001)
        grads_and_vars = optimizer.compute_gradients(model.loss)
        train_op = optimizer.apply_gradients(grads_and_vars, global_step=global_step)
        saver = tf.train.Saver()
        sess.run(tf.initialize_all_variables())


        def train_step(pos_h_batch, pos_t_batch, neg_h_batch, neg_t_batch):
            feed_dict = {
                model.pos_h: pos_h_batch,
                model.pos_t: pos_t_batch,
                model.neg_h: neg_h_batch,
                model.neg_t: neg_t_batch,
            }
            _, step, loss = sess.run([train_op, global_step, model.loss], feed_dict)
            return loss


        for i in range(config.train_times):
            res = 0.0
            for b in range(onto.batch_num):
                ph_batch, pt_batch, nh_batch, nt_batch = onto.getBatch(b)
                los = train_step(ph_batch, pt_batch, nh_batch, nt_batch)
                res += los
                current_step = tf.train.global_step(sess, global_step)
                if b % 1 == 0:
                    print 'batch: %d, loss: %f ' % (b, los)
            print 'train time: %d, loss: %f' % (i, res)

        Exps_order = BagOfEntailments.Exps_order
        ind = 0
        for item in Exps_order:
            print '-------------------------'
            n = len(item)
            print item
            print sess.run(model.ont_embeddings[0, ind:(ind + n)])
            ind += n
            print '-------------------------'

        exps_weights = sess.run(model.ont_embeddings)
        np.savetxt(os.path.join(DIR, s_type + '_Exps_Weights.txt'), exps_weights, '%f')
