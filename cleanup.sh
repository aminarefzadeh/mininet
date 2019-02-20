#!/usr/bin/env bash
# Clean network

sudo ovs-vsctl del-br s1
sudo ovs-vsctl del-br s2

sudo ip link delete s1-eth1
sudo ip link delete s1-eth2
sudo ip link delete s1-eth3
sudo ip link delete s2-eth2

sudo ip netns delete h1
sudo ip netns delete h2
sudo ip netns delete h3