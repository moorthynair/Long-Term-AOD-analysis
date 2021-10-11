file_name =list.files(pattern='.xlsx')
file_name= file_name[-39]
library(readxl)
data = lapply(file_name, function(i){
  k <- read_excel(i)
  k
})
data =do.call('rbind.data.frame',data)
library(tidyverse)
data$DISTRICT=str_to_title(data$DISTRICT)
data[ ,c(1,8,9)] = lapply(data[ ,c(1,8,9)], factor)
j = data %>% group_by(DISTRICT) %>% summarise(mean=median(mean, na.rm=T))
j =arrange(j,mean)
k = j$DISTRICT
m= cat(paste("'",k,"'", sep="",collapse = ","))
data$DISTRICT = factor(data$DISTRICT,
                       levels = c('Rohtas','Bhabua','Gaya','Aurangabad','Arwal','Jahanabad','Pashchim Champaran','Lakhisarai','Buxar','Kishanganj','Nalanda','Sheikhpura','Munger','Bhojpur','Purbi Champaran','Sitamarhi','Khagaria','Muzaffarpur','Madhepura','Supaul','Vaishali','Sheohar','Madhubani','Patna','Begusarai','Saran','Bhagalpur','Purnia','Katihar','Saharsa','Arariya','Samastipur','Gopalganj','Siwan','Darbhanga','Nawada','Banka','Jamui'))

##District wise boxplot in base-R
boxplot(mean~DISTRICT,data,ylab=expression(bold(AOD [0.55~mu*m])), ylim=c(0.1,1.7), las=2, col='#bcb8b1',bg='#bcb8b1',
        font.lab=2, xlab = '', cex.lab=1.5, font.axis=2, cex=1.75,medcol = "red",
        whisklty = 2,outpch = 21, whisklwd=2, boxlwd=2, notch=T, axes=F, outlwd=2)
axis(side=1, at=seq(1,38,1),
, labels = c('Rohtas','Bhabua','Gaya','Aurangabad','Arwal','Jahanabad','Pashchim Champaran','Lakhisarai','Buxar','Kishanganj','Nalanda','Sheikhpura','Munger','Bhojpur','Purbi Champaran','Sitamarhi','Khagaria','Muzaffarpur','Madhepura','Supaul','Vaishali','Sheohar','Madhubani','Patna','Begusarai','Saran','Bhagalpur','Purnia','Katihar','Saharsa','Arariya','Samastipur','Gopalganj','Siwan','Darbhanga','Nawada','Banka','Jamui'),las=2)

axis(side=2, at = seq(0.1,1.8,0.2), labels = seq(0.1,1.8,0.2), las=2)
box()

##District wise boxplot
ggplot(data=data, aes(x=reorder(DISTRICT,mean), y=mean))+stat_boxplot(geom = "errorbar", width = 0.5, size=1.05)+
  geom_boxplot(colour='black',lty=1, size=1.05, fill='white', outlier.size = 3.5, outlier.shape = 21, outlier.stroke = 1.5, outlier.fill = 'blue',notch = TRUE)+theme_bw()+
  stat_summary(fun=mean, geom='point', shape=20,colour='red',size=6)+ylab(expression(bold(AOD [~0.55~mu*m])))+
  scale_y_continuous(breaks = seq(0.1,1.8,0.2),labels = seq(0.1,1.8,0.2))+
  theme(axis.text.x = element_text(colour = 'black', face='bold',size=16,angle=90, vjust=0.3),
        axis.text.y= element_text(colour = 'black', face='bold',size=16), axis.title.y = element_text(colour = 'black', face='bold',size=18),
        axis.title.x = element_blank(), panel.background = element_blank(),panel.border = element_rect(colour = "black",fill=NA),
        axis.ticks = element_line(colour = 'black',size=1.05), axis.ticks.length = unit(.2, "cm"))

##Month wise boxplot
data= data %>% mutate(month=str_sub(month, start=1, end=3))
data$month= factor(data$month, levels = month.abb)
data[ ,c(1,8,9)] = lapply(data[ ,c(1,8,9)], factor)

b=ggplot(data=data, aes(x=month, y=mean))+stat_boxplot(geom = "errorbar", width = 0.5, size=1.05)+
  geom_boxplot(colour='black',lty=1, size=1.05, fill='white', outlier.size = 3.5, outlier.shape = 21, outlier.stroke = 1.5, outlier.fill = 'blue',notch = TRUE)+theme_bw()+
  stat_summary(fun=mean, geom='point', shape=20,colour='red',size=6)+ylab(expression(bold(AOD [~0.55~mu*m])))+
  scale_y_continuous(breaks = seq(0.1,1.8,0.2),labels = seq(0.1,1.8,0.2))+ xlab('Month')+
  theme(axis.text.x = element_text(colour = 'black', face='bold',size=20,angle=0, vjust=0.3),
        axis.text.y= element_text(colour = 'black', face='bold',size=20), axis.title.y = element_text(colour = 'black', face='bold',size=22),
        axis.title.x = element_text(colour = 'black', face='bold',size=22,vjust=-1.2), panel.background = element_blank(),panel.border = element_rect(colour = "black",fill=NA),
        axis.ticks = element_line(colour = 'black',size=1.05), axis.ticks.length = unit(.4, "cm"))

##year wise boxplot
a = ggplot(data=data, aes(x=year, y=mean))+stat_boxplot(geom = "errorbar", width = 0.5, size=1.05)+
  geom_boxplot(colour='black',lty=1, size=1.05, fill='white', outlier.size = 3.5, outlier.shape = 21, outlier.stroke = 1.5, outlier.fill = 'blue',notch = TRUE)+theme_bw()+
  geom_smooth(method='lm', formula = y~x, linetype=1, fill ='8a817c', alpha=0.95, col='darkgreen', aes(group=1), size=1.05, se = FALSE)+
  stat_summary(fun=mean, geom='point', shape=20,colour='red',size=6)+ylab(expression(bold(AOD [~0.55~mu*m])))+
  scale_y_continuous(breaks = seq(0.1,1.8,0.2),labels = seq(0.1,1.8,0.2))+ xlab('Year')+
  theme(axis.text.x = element_text(colour = 'black', face='bold',size=20,angle=90, vjust=0.3),
        axis.text.y= element_text(colour = 'black', face='bold',size=20), axis.title.y = element_text(colour = 'black', face='bold',size=22),
        axis.title.x = element_text(colour = 'black', face='bold',size=22,vjust=-1.2), panel.background = element_blank(),panel.border = element_rect(colour = "black",fill=NA),
        axis.ticks = element_line(colour = 'black',size=1.05), axis.ticks.length = unit(.2, "cm"))

library(ggpubr)
ggarrange(a,b, ncol = 1, nrow=2)

##Seasonwise boxplot
data$seasonal = ifelse(data$month %in% c('Jan','Feb'),'Winter',
                ifelse(data$month %in% c("Mar","Apr",'May'), 'Pre-Monsoon',
                ifelse(data$month %in% c("June","July",'Aug','Sept'), 'Monsoon','Post-Monsoon')))
data$seasonal = factor(data$seasonal, levels = c('Winter','Pre-Monsoon','Monsoon','Post-Monsoon'))
ggplot(data=data, aes(x=seasonal, y=mean))+stat_boxplot(geom = "errorbar", width = 0.5, size=1.05)+
  geom_boxplot(colour='black',lty=1, size=1.05, fill='white', outlier.size = 3.5, outlier.shape = 21, outlier.stroke = 1.5, outlier.fill = 'blue',notch = TRUE)+theme_bw()+
  stat_summary(fun=mean, geom='point', shape=20,colour='red',size=6)+ylab(expression(bold(AOD [~0.55~mu*m])))+
  scale_y_continuous(breaks = seq(0.1,1.8,0.2),labels = seq(0.1,1.8,0.2))+ xlab('Season')+
  theme(axis.text.x = element_text(colour = 'black', face='bold',size=20,angle=0, vjust=0.3),
        axis.text.y= element_text(colour = 'black', face='bold',size=20), axis.title.y = element_text(colour = 'black', face='bold',size=22),
        axis.title.x = element_text(colour = 'black', face='bold',size=22,vjust=-1.2), panel.background = element_blank(),panel.border = element_rect(colour = "black",fill=NA),
        axis.ticks = element_line(colour = 'black',size=1.05), axis.ticks.length = unit(.4, "cm"))

##graphical abstract
forecast <- read_csv("forecast_2020_2021.csv")
forecast = forecast %>% rename('fcast'=1)
forecast = forecast[1:912,]
forecast = forecast %>% separate(period, sep=" ", into=c('month','year'))
forecast[ ,6:8] = lapply(forecast[, 6:8],factor)
ggplot(data=forecast, aes(x=year, y=fcast))+stat_boxplot(geom = "errorbar", width = 0.5, size=1.05)+
  geom_boxplot(colour='black',lty=1, size=1.05, fill='white', outlier.size = 3.5, outlier.shape = 21, outlier.stroke = 1.5, outlier.fill = 'blue',notch = TRUE)+theme_bw()+
  stat_summary(fun=mean, geom='point', shape=20,colour='red',size=6)+ylab(expression(bold(AOD [~0.55~mu*m])))+
  scale_y_continuous(breaks = seq(0.1,1.8,0.2),labels = seq(0.1,1.8,0.2))+ xlab('Year')+
  theme(axis.text.x = element_text(colour = 'black', face='bold',size=16,angle=0, vjust=0.3),
        axis.text.y= element_text(colour = 'black', face='bold',size=16), axis.title.y = element_text(colour = 'black', face='bold',size=18),
        axis.title.x = element_text(colour = 'black', face='bold',size=18,vjust=-1.2), panel.background = element_blank(),panel.border = element_rect(colour = "black",fill=NA),
        axis.ticks = element_line(colour = 'black',size=1.05), axis.ticks.length = unit(.2, "cm"))

##Data availability interpretation using heatmap
library(readxl)
data <- read_excel("data_availability_sheet.xlsx")
View(data)
library(tidyverse)
library(dplyr)
colnames(data)=c('Year','Data_available_percent')
data = separate(data, 'Year', into=c('month','year'))
data$month = substr(data$month,1,3)
data$month = factor(data$month, levels = month.abb)
library(ggplot2)

ggplot(data, aes(x=month, y=year, fill=Data_available_percent))+geom_tile(col='black')+ 
  scale_fill_viridis_c(name='Availability Percent (%)', direction=-1)+
  theme(axis.text = element_text(colour = 'black', face='bold',size=16), axis.title = element_blank(), 
        legend.title = element_text(colour = 'black', face='bold',size=16), legend.text = element_text(colour = 'black', face='bold',size=14))
