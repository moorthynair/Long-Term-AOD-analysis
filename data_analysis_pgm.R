bihar <- read_excel("bihar_state_yearlystat.xlsx")
bihar$year= as.numeric(bihar$year)
ggplot(bihar, aes(x =year, y= mean))+geom_point(fill='red', size=4, shape=22)+theme_bw()+
  geom_errorbar(aes(ymin = percentile_10, ymax= percentile_90), colour='black', size=0.75, linetype =1)+
  geom_smooth(method='lm', formula = y~x, linetype=2, fill ='blue', alpha=0.2, col='darkblue') +
  scale_x_continuous(name='Year', breaks = seq(2000,2020,2), labels =seq(2000,2020,2))+ ylab('AOD')+
  theme(axis.title = element_text(face='bold',color='black',size=18), axis.text = element_text(face='bold',color='black',size=18),
        panel.background = element_blank(), panel.border = element_rect(colour = "black",fill=NA), panel.grid = element_blank())+
  geom_text(aes( x = 2003, y = 0.75, label = paste(round(x$coefficients, digits = 7), " units/year***", sep="")), size=8, fontface='bold')
  
files =list.files(pattern = '.xlsx')
file = lapply(files, function(i){
  data = read_excel(i)
  data
})
data = do.call("rbind.data.frame",file[1:19])
data$year = as.numeric(data$year)
data_new = data %>% filter(DISTRICT == dist[1:19])
ggplot(data_new, aes(x =year, y= mean))+geom_point(fill='red', size=2, shape=22)+theme_bw()+
  geom_errorbar(aes(ymin = percentile_10, ymax= percentile_90), colour='black', size=0.75, linetype =1)+
  geom_smooth(method='lm', formula = y~x, linetype=2, fill ='blue', alpha=0.2, col='darkblue') +
  scale_x_continuous(name='Year', breaks = seq(2000,2020,2), labels =seq(2000,2020,2))+ ylab('AOD')+
  theme(axis.title = element_text(face='bold',color='black',size=12), axis.text = element_text(face='bold',color='black',size=12),
        panel.background = element_blank(), panel.border = element_rect(colour = "black",fill=NA), panel.grid = element_blank())+ facet_wrap(~DISTRICT)+
    geom_text(aes( x = 2003, y = 0.75, label = paste(round(x$coefficients, digits = 7), " units/year***", sep="")), size=8, fontface='bold')

data$DISTRICT = as.factor(data$DISTRICT)
dist = levels(data$DISTRICT)
trend = data.frame(matrix(ncol = 6, nrow = 0))
colnames(trend) =c("district", 'trend_val','mean','sd','coeff_variance', 'p-value')
n=1
combined = lapply(dist, function(i){
  data = data %>% filter(DISTRICT==i)
  y = lm(data$mean~0+data$year)
  trend[n,1]=i
  trend[n,2]= y$coefficients
  trend[n,3]= mean(data$mean)
  trend[n,4]= sd(data$mean)
  trend[n,5] = sd(data$mean)*100/mean(data$mean)
  trend[n,6] = summary(y)$coefficients[,4]
  n=n+1
  trend
})
combined = do.call('rbind.data.frame',combined)


##K-means clustering based on tpwmk for all the districts
annual <- read_excel("MannKendall_sens.xlsx")
month <- read_excel("MannKendall_sens_month.xlsx")
season <- read_excel("MannKendall_sens_seasonal.xlsx")

columns = c('District','mk.tfpwmk_slope','month','season')

cleanup = function(data){
  data = data %>% select(matches(columns))
}

annual =cleanup(annual)
month= cleanup(month)
season=cleanup(season)

##cast the data and then join
month = dcast(month, District~month, value.var = 'mk.tfpwmk_slope')
season = dcast(season, District~season, value.var = 'mk.tfpwmk_slope')
annual = annual %>% rename(annual=2)
comb = Reduce(function(x,y) merge(x,y,by='District',all=TRUE), list(annual,season,month))

library(factoextra)
# scale the data
data_scaled = scale(comb[,-1])
fviz_nbclust(data_scaled, kmeans, method = "wss")+geom_vline(xintercept=4,linetype=2)

library(readxl)
library(tidyverse)
library(dplyr)
library(readr)
file_name = list.files(pattern='*.xlsx')
file_name = file_name[-c(9,10)]
data = lapply(file_name, function(i){
  k = read_excel(i)
  k$dist = i
  k
})

data = do.call('rbind.data.frame',data)
data = data %>% separate(dist, sep=".", into = c('dist','file'), remove=T)

data$type = paste(data$`GHSL-2001`,data$`GHSL-2015`, sep="-")
data$aod_diff = data$`AOD-2015`-data$`AOD-2001` 
data = data[ ,c(6,5,9,10)]
data_hclust = data %>% pivot_wider(names_from = type, values_from = c(aod_diff,count))


##forecasted data analysis
library(readr)
data <- read_csv("forecast_2020_2021.csv")
View(data)

data = data %>% separate(period, into=c('month','year'), remove=T)
data$year = as.factor(data$year)
data %>% group_by(year) %>% summarise(max= min(`Point Forecast`))
data_final = data[c(1:912),] %>% group_by(year,dist) %>% summarise_at(vars(`Lo 95`,`Hi 95`), funs(mean(.,na.rm=T)))
data_final = data_final %>% pivot_wider(names_from = year, values_from = c(`Lo 95`,`Hi 95`))
data_final$dist = str_to_title(data_final$dist)

data_final = data[c(1:912),] %>% group_by(year,dist) %>% summarise(mean = mean(`Point Forecast`))
data_final = data_final %>% mutate(percent = (mean-0.67)*100/0.67)

data_final$dist [which.max(data_final$mean[data_final$year==2021])]
data_final$dist[(data_final$mean >= 0.67) & (data_final$year==2020)] [which.min(data_final$percent[(data_final$mean >= 0.67) & (data_final$year==2020)])]
data_final=data_final %>% pivot_wider(names_from = year, values_from=mean)
data_2019 <- read_excel("2019.xlsx")
data_2019 = data_2019[, c(1,4)]
data_2019 = data_2019 %>% rename('2019'=2, dist=1)

final = merge(data_final, data_2019[1:38, ], by='dist')
percent = function(x){((x-final$`2019`)*100/final$`2019`)}
final1= final %>% mutate_at(vars('2020','2021'), funs(percent))
final$inter = (final$`2021`-final$`2020`)*100/final$`2020`
library(readr)
mk <- read_csv("G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_facets_savgol_updated/mk_openair_deseason.csv")
View(mk)
mk = mk[, c(6,7)]
final = merge(final,mk, by='dist')
write.table(final,file='arima.csv',sep=",", row.names = FALSE)


## perasons correlation

##input the forecasted data
library(readr)
forecast <- read_csv("forecast_2020_2021.csv")
View(forecast)

forecast = separate(forecast, col=period,into=c('month', 'year'))
forecast = forecast %>% filter(year==2020)
forecast = forecast %>% select(1,6:8)
forecast = forecast %>% mutate_if(is.character, factor)
forecast = forecast %>% mutate_if(is.factor,str_to_title)

##input original AOD value
files = list.files(pattern = '.xlsx')
data = lapply(files, function(i){
  k = read_excel(i)
  k = k%>% select(1,4,8) %>% separate(month, sep='-',into =c('month','year'))
  k
})

data = do.call('rbind.data.frame',data)
data = data %>% mutate_if(is.character, factor)
data = data %>% mutate_if(is.factor,str_to_title)

##input bihar monthly data
library(readxl)
monthly_bihar <- read_excel("monthly_bihar.xlsx")
View(monthly_bihar)
monthly_bihar=monthly_bihar %>% select(3,7,8)
monthly_bihar = monthly_bihar %>% separate(month, sep="-", into= c('month','year'))
data = rbind(data,monthly_bihar)


final = merge(data,forecast, by.x =c('DISTRICT','month','year'), by.y = c('dist','month','year'))
final=final %>% mutate_if(is.character, factor)

##collect correlation values
data_collect = data.frame(matrix(ncol=2))
colnames(data_collect)= c('district','corr')

dist = levels(final$DISTRICT)
n=1
corr_dist = lapply(dist, function(i){
  final = final %>% filter(DISTRICT==i)
  data_collect[n,1] = as.character(i)
  data_collect[n,2] = cor(final$mean,final$`Point Forecast`)
  n=n+1
  data_collect
})
data_collect = do.call('rbind.data.frame',corr_dist)
cor(final$mean,final$`Point Forecast`)


##correlation monthwise
month_list = levels(final$month)
data_month = data.frame(matrix(ncol=2))
colnames(data_month)= c('month','corr')

corr_dist = lapply(month_list, function(i){
  final = final %>% filter(month==i)
  data_month$month = as.character(i)
  data_month$corr = cor(final$mean,final$`Point Forecast`)
  data_month
})
data_month = do.call('rbind.data.frame',corr_dist)
data_month = data_month %>% arrange(desc(corr))
data_collect = data_collect %>% arrange(desc(corr))

write.table(data_collect, file = 'dist_corr.csv',sep=",",row.names = F)
write.table(data_month, file = 'month_corr.csv',sep=",",row.names = F)
