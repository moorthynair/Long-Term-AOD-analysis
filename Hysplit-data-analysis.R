##Hysplit analysis

data = list.files(pattern=".RData")
traj = lapply(data, function(i){
  load(i)
  traj_NS
})

traj = do.call('rbind.data.frame',traj)
library(openair)
library(dplyr)
traj$study_month =as.numeric(format(traj$date,'%m')) 
traj$study_year =as.numeric(format(traj$date,'%Y'))

filename = paste(month.abb,'.png',sep="")
month = seq(1,12,1)

lapply(month, function(i){
png(filename[i],width = 650, height = 400, units = "px")
trajLevel(traj %>% filter(study_month==i), statistic = "frequency",plot = TRUE,  split.after = FALSE, map.fill = FALSE, map.cols = "black", map.alpha = 2, projection = "mercator", parameters = NULL, orientation = c(90,0,0), by.type = TRUE, origin = TRUE, lwd=4, grid.col="transparent", grid.alpha=0.4, font.label= c(12, "bold", "red"), par.settings=list(fontsize=list(text=16)), xlim=c(50,100),ylim=c(-10,50))
dev.off()
})


lapply(month, function(i){
  png(filename[i],width = 650, height = 400, units = "px")
  trajLevel(traj %>% filter(study_month==i), method = "hexbin", col = "jet" , plot = TRUE,  split.after = FALSE, map.fill = FALSE, map.cols = "black", map.alpha = 2, projection = "mercator", parameters = NULL, orientation = c(90,0,0), by.type = TRUE, origin = TRUE, lwd=4, grid.col="transparent", grid.alpha=0.4, font.label= c(12, "bold", "red"), par.settings=list(fontsize=list(text=16)), xlim=c(50,100),ylim=c(-10,50))
  dev.off()
  })

trajPlot(traj_NS ,group='season', projection="cylindrical", orientation=c(90,90,0), parameters=NULL, grid.col = "transparent", map.fill = FALSE)

trajLevel(traj %>% filter(study_month==9), method = "hexbin", col = "jet" , projection="cylindrical", orientation=c(90,90,0), parameters=NULL, grid.col = "transparent", map.fill = FALSE,grid.col="transparent", grid.alpha=0.4, font.label= c(12, "bold", "red"), par.settings=list(fontsize=list(text=16)), xlim=c(50,100),ylim=c(-10,50))

trajLevel(traj_NS,  statistic = "frequency", plot = TRUE,  split.after = FALSE, map.fill = FALSE, map.cols = "transparent", map.alpha =1, projection = "mercator", parameters = NULL, orientation = c(90,0,0), by.type = TRUE, origin = TRUE, lwd=12, grid.col="transparent", grid.alpha=0.4, font.label= c(12, "bold", "red"), par.settings=list(fontsize=list(text=16)), xlim=c(50,100),ylim=c(-10,50))


trajCluster(traj , method = "Euclid", type='year',  plot = TRUE,  split.after = FALSE, map.fill = TRUE, map.cols = "grey", map.alpha = 0.2, projection = "mercator", parameters = NULL, orientation = c(90,90,0), by.type = TRUE, origin = TRUE, lwd=6, grid.col="transparent", grid.alpha=0.2, font.label= c(12, "bold", "red"),  par.settings=list(fontsize=list(text=10, face=2)), xlim=c(50,100),ylim=c(-10,50))

trajCluster(traj_NS, method = "Euclid", n.cluster = 4, cols = c("red", "red", "red", "red"), plot = TRUE,  split.after = FALSE, map.fill = FALSE, map.cols = "transparent", map.alpha = 1, projection = "mercator", parameters = NULL, orientation = c(90,0,0), by.type = TRUE, origin = TRUE, lwd=2, grid.col="transparent", grid.alpha=0.4, font.label= c(12, "bold", "red"), par.settings=list(fontsize=list(text=12)), xlim=c(30,100),ylim=c(05,40), xlab='',ylab='')

##create basemap
z1=maps::map(maptools::readShapePoly("C:/Users/USER/Desktop/Hysplit/World-India/india_map"), plot=FALSE)
# create internal representation
z2=mapMaker::map.make(z1)
# write binary files:
mapMaker::map.export.bin(z2, "C:/Users/USER/Desktop/Hysplit/World-India/world")

library(maps)
worldMapEnv="MYMAP"
Sys.setenv("MYMAP"="C:/Users/USER/Desktop/Hysplit/World-India/")
map("world", lwd=2)
