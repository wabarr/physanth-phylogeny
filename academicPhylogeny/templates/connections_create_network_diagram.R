require(igraph)
require(ggplot2)
require(RCurl)

eval( expr = parse( text = getURL("https://dl.dropboxusercontent.com/u/1648032/AcademicPhylogeny/ggGraphPlot.R")))

links<-read.table("/home/wabarr/webapps/django/myproject/myproject/academicPhyloConnectionsForR.txt",na.strings="None",header=TRUE,sep=",")
linksSimple<-data.frame(from=paste(links$AdvisorFirstName,links$AdvisorLastName,sep=" "),
                        to=paste(links$StudentFirstName,links$StudentLastName,sep=" "))
g=graph.data.frame(linksSimple)

thePlot<-ggGraphPlot(g,layout=layout.kamada.kawai(g),labelSize=1.3)
ggsave(filename="/home/wabarr/webapps/static/images/currentNetwork.jpg",plot=thePlot,width=3.5,height=3.5,units="in")
