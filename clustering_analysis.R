library(readr)
data1 <- read_csv("mk_openair_seasonal.csv")
View(data1)
library(tidyverse)
library(dplyr)

library(readr)
dist_data <- read_csv("mk_openair_deseason.csv")
View(dist_data)
dist_data = dist_data[-40,c(3,7)]
colnames(dist_data)= c('long_term','dist')

data = data1[,c(3,7,8)]
data = data %>% pivot_wider(names_from = season, values_from = c(slope))
data = merge(data,dist_data, by='dist')
row.names(data)=data$dist
data = data[-9,-1]


##feature scaling
m = apply(data,2,mean)
sd= apply(data,2,sd)
z = scale(data,m,sd)

scale_mean = apply(z,1,mean)

##clustering
dist = dist(z)
hclust = hclust(dist, method='complete')
plot(hclust, hang=-1)
rect.hclust(hclust, k=2, border=2:3)

##cutree
h_member = cutree(hclust,2)
sil = silhouette(cutree(hclust,2),dist)
rownames(sil) = rownames(data)
plot(sil, font=2, cex=0.6)

