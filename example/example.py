from __future__ import division
import caffe
import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt

def center_crop(im):
  
  sz = im.shape[0:-1]
  side_length = np.min(sz)
  if sz[0] > sz[1]:
    ul_x = 0  
    ul_y = np.floor((sz[0]/2) - (side_length/2))
    x_inds = [ul_x, sz[1]-1]
    y_inds = [ul_y, ul_y+side_length-1]
  else:
    ul_x = np.floor((sz[1]/2) - (side_length/2))
    ul_y = 0
    x_inds = [ul_x, ul_x+side_length-1]
    y_inds = [ul_y, sz[0]-1]

  c_im = im[y_inds[0]:y_inds[1]+1, x_inds[0]:x_inds[1]+1, :]

  return c_im, [c_im.shape, x_inds, y_inds]

def preprocess(im, caffe_sz):
  
  # scale to [0, 255] 
  im = (255*im).astype(np.float32, copy=False)

  # channel swap (RGB -> BGR)
  im = im[:, :, [2,1,0]]
  
  # make caffe size
  im = caffe.io.resize_image(im, caffe_sz)

  # subtract mean 
  im = im - np.asarray([104,117,123]).reshape((1,1,3))
  
  # make channels x height x width
  im = im.swapaxes(0,2).swapaxes(1,2)
 
  caffe_input = im.reshape((1,)+im.shape)
 
  return caffe_input

def bin2val(bin_id, bin_edges):
  assert 0 <= bin_id < bin_edges.size-1, 'impossible bin_id'

  # handle infinite bins, choose left/right edge as appropriate
  if bin_id == 0 and bin_edges[0] == -np.inf:
    val = bin_edges[1]
  elif bin_id == bin_edges.size-2 and bin_edges[-1] == np.inf:
    val = bin_edges[-2]
  else:
    val = (bin_edges[bin_id] + bin_edges[bin_id+1]) / 2

  return val

def extrap_horizon(left, right, width):
  
  hl_homo = np.cross(np.append(left, 1), np.append(right, 1))
  hl_left_homo = np.cross(hl_homo, [-1, 0, -width/2]);
  hl_left = hl_left_homo[0:2]/hl_left_homo[-1];
  hl_right_homo = np.cross(hl_homo, [-1, 0, width/2]);
  hl_right = hl_right_homo[0:2]/hl_right_homo[-1];
  
  return hl_left, hl_right

def compute_horizon(slope_dist, offset_dist, caffe_sz, sz, crop_info, bin_edges):
  
  # setup
  crop_sz, x_inds, y_inds = crop_info

  # get maximum bin
  slope_bin = np.argmax(slope_dist)
  offset_bin = np.argmax(offset_dist)
  
  # compute (slope, offset)
  slope = bin2val(slope_bin, bin_edges['slope_bin_edges']) 
  offset = bin2val(offset_bin, bin_edges['offset_bin_edges'])
  
  # (slope, offset) to (left, right)
  offset = offset * caffe_sz[0]
  c = offset / np.cos(np.abs(slope))
  caffe_left = -np.tan(slope)*caffe_sz[1]/2 + c
  caffe_right = np.tan(slope)*caffe_sz[1]/2 + c

  # scale back to cropped image
  c_left = caffe_left * (crop_sz[0] / caffe_sz[0])
  c_right = caffe_right * (crop_sz[0] / caffe_sz[0])

  # scale back to original image
  center = [(sz[1]+1)/2, (sz[0]+1)/2]
  crop_center = [np.dot(x_inds,[.5, .5])-center[0], center[1]-np.dot(y_inds,[.5, .5])]
  left_tmp = np.asarray([-crop_sz[1]/2, c_left]) + crop_center 
  right_tmp = np.asarray([crop_sz[1]/2, c_right]) + crop_center 
  left, right = extrap_horizon(left_tmp, right_tmp, sz[1])

  return [np.squeeze(left), np.squeeze(right)]


if __name__ == '__main__': 
 
  # image credit:
  # https://commons.wikimedia.org/wiki/File:HFX_Airport_4.jpg
  fname = 'airport.jpg'

  # load bin edges
  bin_edges = sio.loadmat('bins.mat')

  # load network
  deploy_file = '../models/classification/so_places/deploy.net'
  model_file = '../models/classification/so_places/so_places.caffemodel'
  caffe.set_mode_cpu()
  net = caffe.Net(deploy_file, model_file, caffe.TEST)
  caffe_sz = np.asarray(net.blobs['data'].shape)[2:]

  # preprocess image 
  im = caffe.io.load_image(fname)
  sz = im.shape
  center_im, crop_info = center_crop(im) 
  caffe_input = preprocess(center_im, caffe_sz)

  # push through the network
  result = net.forward(data=caffe_input, blobs=['prob_slope', 'prob_offset'])
  slope_dist = result['prob_slope'][0]
  offset_dist = result['prob_offset'][0]

  # convert distributions to horizon line 
  left, right = compute_horizon(slope_dist, offset_dist, caffe_sz, sz, crop_info, bin_edges)
  print left[1], right[1] 
 
  plt.figure(1)
  plt.imshow(im, extent=[-sz[1]/2, sz[1]/2, -sz[0]/2, sz[0]/2])
  plt.plot([left[0], right[0]], [left[1], right[1]], 'r')
  ax = plt.gca();
  ax.autoscale_view('tight')
  plt.show()
