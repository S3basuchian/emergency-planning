/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/ndnSIM-module.h"

namespace ns3 {

int
main(int argc, char* argv[])
{
  // setting default parameters for PointToPoint links and channels
  Config::SetDefault("ns3::PointToPointNetDevice::DataRate", StringValue("1Mbps"));
  Config::SetDefault("ns3::PointToPointChannel::Delay", StringValue("10ms"));
  Config::SetDefault("ns3::DropTailQueue<Packet>::MaxSize", StringValue("20p"));

  // Read optional command-line parameters (e.g., enable visualizer with ./waf --run=<> --visualize
  CommandLine cmd;
  cmd.Parse(argc, argv);

  // Creating nodes
  NodeContainer nodes;
  nodes.Create(13);

  // Connecting nodes using two links
  PointToPointHelper p2p;
  p2p.Install(nodes.Get(0), nodes.Get(5));
  p2p.Install(nodes.Get(1), nodes.Get(5));
  p2p.Install(nodes.Get(2), nodes.Get(5));
  p2p.Install(nodes.Get(3), nodes.Get(6));
  p2p.Install(nodes.Get(4), nodes.Get(6));
  p2p.Install(nodes.Get(5), nodes.Get(7));
  p2p.Install(nodes.Get(6), nodes.Get(7));
  p2p.Install(nodes.Get(7), nodes.Get(8));
  p2p.Install(nodes.Get(7), nodes.Get(9));
  p2p.Install(nodes.Get(8), nodes.Get(10));
  p2p.Install(nodes.Get(8), nodes.Get(11));
  p2p.Install(nodes.Get(9), nodes.Get(12));

  // Install NDN stack on all nodes
  ndn::StackHelper ndnHelper;
  ndnHelper.SetDefaultRoutes(true);
  ndnHelper.setPolicy("nfd::cs::lru");
  ndnHelper.setCsSize(10);
  ndnHelper.Install(nodes.Get(0));
  ndnHelper.Install(nodes.Get(1));
  ndnHelper.Install(nodes.Get(2));
  ndnHelper.Install(nodes.Get(3));
  ndnHelper.Install(nodes.Get(4));
  ndnHelper.Install(nodes.Get(5));
  ndnHelper.Install(nodes.Get(6));
  ndnHelper.Install(nodes.Get(8));
  ndnHelper.Install(nodes.Get(9));
  ndnHelper.Install(nodes.Get(10));
  ndnHelper.Install(nodes.Get(11));
  ndnHelper.Install(nodes.Get(12));
  ndnHelper.setPolicy("nfd::cs::rl");
  ndnHelper.setCsSize(18);
  ndnHelper.Install(nodes.Get(7));


  // Choosing forwarding strategy
  ndn::StrategyChoiceHelper::InstallAll("/movie", "/localhost/nfd/strategy/multicast");
  ndn::StrategyChoiceHelper::InstallAll("/news", "/localhost/nfd/strategy/multicast");
  ndn::StrategyChoiceHelper::InstallAll("/gov", "/localhost/nfd/strategy/multicast");

  // Installing applications

  // Consumer
  ndn::AppHelper consumerHelper("ns3::ndn::ConsumerCbr");
  consumerHelper.SetPrefix("/movie/lotr");
  consumerHelper.SetAttribute("Frequency", StringValue("5"));
  consumerHelper.Install(nodes.Get(0));
  consumerHelper.SetPrefix("/news/15-08");
  consumerHelper.SetAttribute("Frequency", StringValue("2"));
  consumerHelper.Install(nodes.Get(1));
  consumerHelper.SetPrefix("/news/14-08");
  consumerHelper.SetAttribute("Frequency", StringValue("3"));
  consumerHelper.Install(nodes.Get(2));
  consumerHelper.SetPrefix("/news/14-08");
  consumerHelper.SetAttribute("Frequency", StringValue("1"));
  consumerHelper.Install(nodes.Get(3));
  consumerHelper.SetPrefix("/gov/emergency");
  consumerHelper.SetAttribute("Frequency", StringValue("1"));
  auto apps = consumerHelper.Install(nodes.Get(4));
  apps.Stop(Seconds(20.0)); 
  
  
  // Producer
  ndn::AppHelper producerHelper("ns3::ndn::Producer");
  producerHelper.SetPrefix("/movie");
  producerHelper.SetAttribute("PayloadSize", StringValue("1024"));
  producerHelper.Install(nodes.Get(10)); 
  producerHelper.SetPrefix("/news");
  producerHelper.SetAttribute("PayloadSize", StringValue("1024"));
  producerHelper.Install(nodes.Get(11)); 
  producerHelper.SetPrefix("/gov");
  producerHelper.SetAttribute("PayloadSize", StringValue("1024"));
  producerHelper.Install(nodes.Get(12)); 

  Simulator::Stop(Seconds(30.0));

  Simulator::Run();
  Simulator::Destroy();

  return 0;
}

} // namespace ns3

int
main(int argc, char* argv[])
{
  return ns3::main(argc, argv);
}
