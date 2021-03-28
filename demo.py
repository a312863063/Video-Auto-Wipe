# -*- coding: utf-8 -*-
'''
Copyright: Copyright(c) 2018, seeprettyface.com, BUPT_GWY contributes the model.
Thanks to STTN provider: https://github.com/researchmm/STTN
Author: BUPT_GWY
Contact: a312863063@126.com
'''
import cv2
import numpy as np
import importlib
import argparse
import sys
import torch
import os
from torchvision import transforms

# My libs
from core.utils import Stack, ToTorchFormatTensor

parser = argparse.ArgumentParser(description="STTN")

parser.add_argument("-t", "--task", type=str, help='CHOOSE THE TASK：delogo or detext', default='detext')
parser.add_argument("-v", "--video", type=str, default='input/detext_examples/chinese1.mp4')
parser.add_argument("-m", "--mask",  type=str, default='input/detext_examples/mask/chinese1_mask.png')
parser.add_argument("-r", "--result",  type=str, default='result/')
parser.add_argument("-d", "--dual",  type=bool, default=False, help='Whether to display the original video in the final video')
parser.add_argument("-w", "--weight",   type=str, default='pretrained-weight/detext_trial.pth')

parser.add_argument("--model", type=str, default='auto-sttn')
parser.add_argument("-g", "--gap",   type=int, default=200, help='set it higher and get result better')
parser.add_argument("-l", "--ref_length",   type=int, default=5)
parser.add_argument("-n", "--neighbor_stride",   type=int, default=5)

args = parser.parse_args()

_to_tensors = transforms.Compose([
    Stack(),
    ToTorchFormatTensor()])

def read_frame_info_from_video(vname):
    reader = cv2.VideoCapture(vname)
    if not reader.isOpened():
        print("fail to open video in {}".format(args.input))
        sys.exit(1)
    frame_info = {}
    frame_info['W_ori'] = int(reader.get(cv2.CAP_PROP_FRAME_WIDTH) + 0.5)
    frame_info['H_ori'] = int(reader.get(cv2.CAP_PROP_FRAME_HEIGHT) + 0.5)
    frame_info['fps'] = reader.get(cv2.CAP_PROP_FPS)
    frame_info['len'] = int(reader.get(cv2.CAP_PROP_FRAME_COUNT) + 0.5)
    return reader, frame_info

def read_mask(path):
    img = cv2.imread(path, 0)
    ret, img = cv2.threshold(img, 127, 1, cv2.THRESH_BINARY)
    img = img[:, :, None]
    return img

# sample reference frames from the whole video
def get_ref_index(neighbor_ids, length):
    ref_index = []
    for i in range(0, length, args.ref_length):
        if not i in neighbor_ids:
            ref_index.append(i)
    return ref_index

def pre_process(task):
    print('Task: ', task)
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    net = importlib.import_module('model.' + args.model)
    model = net.InpaintGenerator().to(device)
    data = torch.load(args.weight, map_location=device)
    model.load_state_dict(data['netG'])
    model.eval()
    print('Loading weight from: {}'.format(args.weight))

    # prepare dataset, encode all frames into deep space
    reader, frame_info = read_frame_info_from_video(args.video)
    if not os.path.exists(args.result):
        os.makedirs(args.result)
    video_base_name = os.path.join(args.result, os.path.basename(args.video).rsplit('.', 1)[0])
    video_name = f"{video_base_name}_{task}.mp4"
    video_H = frame_info['H_ori'] if not args.dual else frame_info['H_ori'] * 2
    writer = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc(*"mp4v"), frame_info['fps'], (frame_info['W_ori'], video_H))
    print('Loading video from: {}'.format(args.video))
    print('Loading mask from: {}'.format(args.mask))
    print('--------------------------------------')

    clip_gap = args.gap  # processing how many frames during one period
    rec_time = frame_info['len'] // clip_gap if frame_info['len'] % clip_gap == 0 else frame_info['len'] // clip_gap + 1
    mask = read_mask(args.mask)
    return clip_gap, device, frame_info, mask, model, reader, rec_time, video_name, writer

def process(frames, model, device, w, h):
    video_length = len(frames)
    feats = _to_tensors(frames).unsqueeze(0) * 2 - 1

    feats = feats.to(device)
    comp_frames = [None] * video_length

    with torch.no_grad():
        feats = model.encoder(feats.view(video_length, 3, h, w))
        _, c, feat_h, feat_w = feats.size()
        feats = feats.view(1, video_length, c, feat_h, feat_w)

    # completing holes by spatial-temporal transformers
    for f in range(0, video_length, args.neighbor_stride):
        neighbor_ids = [i for i in range(max(0, f - args.neighbor_stride), min(video_length, f + args.neighbor_stride + 1))]
        ref_ids = get_ref_index(neighbor_ids, video_length)
        with torch.no_grad():
            pred_feat = model.infer(
                feats[0, neighbor_ids + ref_ids, :, :, :])
            pred_img = torch.tanh(model.decoder(
                pred_feat[:len(neighbor_ids), :, :, :])).detach()
            pred_img = (pred_img + 1) / 2
            pred_img = pred_img.cpu().permute(0, 2, 3, 1).numpy() * 255
            for i in range(len(neighbor_ids)):
                idx = neighbor_ids[i]
                img = np.array(pred_img[i]).astype(
                    np.uint8)
                if comp_frames[idx] is None:
                    comp_frames[idx] = img
                else:
                    comp_frames[idx] = comp_frames[idx].astype(
                        np.float32) * 0.5 + img.astype(np.float32) * 0.5
    return comp_frames

def get_inpaint_mode_for_detext(H, h, mask):  # get inpaint segment
    mode = []
    to_H = from_H = H   # the subtitles are usually underneath
    while from_H != 0:
        if to_H - h < 0:
            from_H = 0
            to_H = h
        else:
            from_H = to_H - h
        if not np.all(mask[from_H:to_H, :] == 0) and np.sum(mask[from_H:to_H, :]) > 10:
            if to_H != H:
                move = 0
                while to_H + move < H and not np.all(mask[to_H+move, :] == 0):
                    move += 1
                if to_H + move < H and move < h:
                    to_H += move
                    from_H += move
            mode.append((from_H, to_H))
        to_H -= h
    return mode

def main():  # detext
    # set up models
    w, h = 640, 120
    clip_gap, device, frame_info, mask, model, reader, rec_time, video_name, writer = pre_process(args.task)

    split_h = int(frame_info['W_ori'] * 3 / 16)
    mode = get_inpaint_mode_for_detext(frame_info['H_ori'], split_h, mask)

    for i in range(rec_time):
        start_f = i * clip_gap
        end_f = min((i + 1) * clip_gap, frame_info['len'])
        print('Processing:', start_f+1, '-', end_f, ' / Total:', frame_info['len'])

        frames_hr = []
        frames = {}
        comps = {}
        for k in range(len(mode)):
            frames[k] = []
        for j in range(start_f, end_f):
            success, image = reader.read()
            frames_hr.append(image)
            for k in range(len(mode)):
                image_crop = image[mode[k][0]:mode[k][1], :, :]
                image_resize = cv2.resize(image_crop, (w, h))
                frames[k].append(image_resize)

        for k in range(len(mode)):
            comps[k] = process(frames[k], model, device, w, h)

        if mode is not []:
            for j in range(end_f - start_f):
                frame_ori = frames_hr[j].copy()
                frame = frames_hr[j]
                for k in range(len(mode)):
                    comp = cv2.resize(comps[k][j], (frame_info['W_ori'], split_h))
                    comp = cv2.cvtColor(np.array(comp).astype(np.uint8), cv2.COLOR_BGR2RGB)
                    mask_area = mask[mode[k][0]:mode[k][1], :]
                    frame[mode[k][0]:mode[k][1], :, :] = mask_area * comp + (1 - mask_area) * frame[mode[k][0]:mode[k][1], :, :]
                if args.dual:
                    frame = np.vstack([frame_ori, frame])
                writer.write(frame)

    writer.release()
    print('--------------------------------------')
    print('Finish in {}'.format(video_name))

if __name__ == '__main__':
    main()
