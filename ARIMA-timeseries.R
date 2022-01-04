##Time series forecasting using Auto Regressive Integrate Moving Average technique (ARIMA)

library(caret)
library(readxl)
library(forecast)
library(tidyverse)
library(MLmetrics)
library(lmtest)

data = list.files(pattern = '.xlsx')
which(data =="bihar_state_stat.xlsx")
data =data[-39]
aod_data = lapply(data,function(i){
  data = read_excel(i)
  data$period = i
  data$month = str_sub(data$month, start=1, end=3)
  data$month = factor(data$month, levels = month.abb)
  data
})

aod_data = do.call('rbind.data.frame',aod_data)
head(aod_data, 5)
str(aod_data)
aod_data = aod_data %>% mutate_if(is.character,factor)
aod_data = arrange(aod_data, year, month)

dist= levels(aod_data$DISTRICT)

dist_data = aod_data%>% filter(DISTRICT=='JAMUI') 
data_ts =ts(dist_data$mean, start =c(2001,1), frequency=12)
data_arima = auto.arima(data_ts, seasonal = TRUE,
                        ic = c("aicc", "aic", "bic"),
                        stepwise = F,
                        trace = F,
                        approximation = F,
                        allowdrift = TRUE)
data_arima_forecast = forecast(data_arima, h=24)
sumary_arima = summary(data_arima)
MAPE(data_arima$fitted, data_arima$x)
rsq(data_arima$fitted, data_arima$x)
resd = checkresiduals(data_arima)


##R-Squared function
rsq = function (x,y) cor(x,y)^2

ts_para = do.call('rbind.data.frame',k)
 
ts_para = na.omit(ts_para)

k =lapply(dist,function(i){
    dist_data = aod_data %>% filter(DISTRICT==i)
  data_ts =ts(dist_data$mean, start =c(2001,1), frequency=12)
  data_arima = auto.arima(data_ts, seasonal = TRUE,
                          ic = c("aicc", "aic", "bic"),
                          stepwise = F,
                          trace = F,
                          approximation = F,
                          allowdrift = TRUE)
  sumary_arima = summary(data_arima)
  resd = checkresiduals(data_arima)
  data_arima_forecast = forecast(data_arima, h=24)
  ts_para = data.frame(matrix())
  ts_para$dist =i
  ts_para$rsq = rsq(data_arima$fitted, data_arima$x)
  ts_para$mape = sumary_arima[5]
  ts_para$rmse = sumary_arima[2]
  ts_para$p=data_arima$arma[1]
  ts_para$q=data_arima$arma[2]
  ts_para$P=data_arima$arma[3]
  ts_para$Q=data_arima$arma[4]
  ts_para$d=data_arima$arma[6]
  ts_para$D=data_arima$arma[7]
  ts_para$S=data_arima$arma[5]
  ts_para$bic = data_arima$bic
  ts_para$aic = data_arima$aic
  ts_para$aicc = data_arima$aicc
  ts_para$loglik= data_arima$loglik
  ts_para$sd = sqrt(data_arima$sigma2)
  ts_para$stat_LB = resd[1]
  ts_para$df_LB = resd[2]
  ts_para$pval_LB = resd[3]
  ts_para$sigma2 = as.numeric(data_arima$sigma2)
  ts_para
})


ts_para = do.call('rbind.data.frame',k)
ts_para$stat_LB = str_remove_all(ts_para$stat_LB, pattern = "[c(`Q*` = )]")
ts_para$df_LB = str_remove_all(ts_para$df_LB, pattern = "[c(`Q*` = df)]")
ts_para = ts_para[,-1]
ts_para$model= paste("(",ts_para$p,",",ts_para$d,",",ts_para$q,")",'(',ts_para$P,",",
                 ts_para$D,",",ts_para$Q,")","[",ts_para$S,"]", sep = "")

ts_para$pval_LB = as.numeric(ts_para$pval_LB)
write.table(ts_para,
            file='G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_facets_savgol_updated/arima_forecasted/ts_parameters.csv', row.names=F, sep=",")


##save the individual forecasted values
k = lapply(dist,function(i){
  dist_data = aod_data %>% filter(DISTRICT==i)
  data_ts =ts(dist_data$mean, start =c(2001,1), frequency=12)
  data_arima = auto.arima(data_ts, seasonal = TRUE,
                          ic = c("aicc", "aic", "bic"),
                          stepwise = F,
                          trace = F,
                          approximation = F,
                          allowdrift = TRUE)
  data_arima_forecast = forecast(data_arima, h=24)
  forecasted_ts = as.data.frame(data_arima_forecast)
  forecasted_ts$period = rownames(forecasted_ts)
  forecasted_ts$dist =i
  rownames(forecasted_ts)=NULL
  forecasted_ts
})
ts_para = do.call('rbind.data.frame',k)
write.table(ts_forecast_2020_2021_final,
            file='G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_facets_savgol_updated/arima_forecasted/forecast_2020_2021.csv', row.names=F, sep=",")

##derive the mean fitted value (2001-2019) from the basic forecasted mod
k =lapply(dist,function(i){
  dist_data = aod_data %>% filter(DISTRICT==i)
  data_ts =ts(dist_data$mean, start =c(2001,1), frequency=12)
  data_arima = auto.arima(data_ts, seasonal = TRUE,
                          ic = c("aicc", "aic", "bic"),
                          stepwise = F,
                          trace = F,
                          approximation = F,
                          allowdrift = TRUE)
  forcast_mod = as.data.frame(as.numeric(data_arima$fitted))
  colnames(forcast_mod)= 'fitted'
  forcast_mod$dist =i
  forcast_mod$period = rep(seq(2001,2019,1),each=12)
  forcast_mod
 })
ts_para = do.call('rbind.data.frame',k)
write.table(fitted_cbind,
            file='G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_facets_savgol_updated/arima_forecasted/fitted.csv', row.names=F, sep=",")

##All the configures/analysed data shifted to another data file
fitted=ts_para
ts_parameters = ts_para
ts_forecast_2020_2021 = ts_para

##timeseries analysis for Bihar State
bihar <- read_excel("bihar_state_stat.xlsx")
bihar_ts =ts(bihar$mean, start =c(2001,1), frequency=12)
data_arima = auto.arima(bihar_ts, seasonal = TRUE,
                        ic = c("aicc", "aic", "bic"),
                        stepwise = F,
                        trace = F,
                        approximation = F,
                        allowdrift = TRUE)
forcast_mod = as.data.frame(as.numeric(data_arima$fitted))
colnames(forcast_mod)= 'fitted'
forcast_mod$dist ='BIHAR'
forcast_mod$period = rep(seq(2001,2019,1),each=12)
##rbind district date with Bihar data
fitted_cbind= rbind(fitted,forcast_mod)
data_arima_forecast = forecast(data_arima, h=24)
forecasted_ts = as.data.frame(data_arima_forecast)
forecasted_ts$period = rownames(forecasted_ts)
forecasted_ts$dist ='BIHAR'
rownames(forecasted_ts)=NULL
##rbind district date with Bihar data
ts_forecast_2020_2021_final = rbind(ts_forecast_2020_2021,forecasted_ts)
accuracy(data_arima)

##generate facet plot for forecasted data
library(readr)
forecast <- read_csv("forecast_2020_2021.csv")
View(forecast)
library(stringr)
library(dplyr)
library(tidyverse)
forecast = forecast %>% separate(period, into=c('month','year'),remove=T, sep=" ")
forecast = forecast %>% mutate_if(is.character, factor)
forecast$dist = str_to_title(forecast$dist)
forecast_mean = aggregate(cbind(`Point Forecast`,`Lo 80`,`Hi 80`,`Lo 95`,`Hi 95`)~dist+year, 
                          forecast, mean, na.rm=T)

library(ggplot2)
colnames(forecast)
forecast$month = factor(forecast$month, levels = month.abb)

ggplot(forecast, aes(x=reorder(dist,`Point Forecast`, FUN=mean), y=`Point Forecast`))+
  stat_boxplot(geom = "errorbar", width = 0.5, size=1.05)+
  geom_boxplot(colour='black',lty=1, size=1.05, fill='white', outlier.size = 3.5, outlier.shape = 21, outlier.stroke = 1.5, outlier.fill = 'blue',notch = TRUE, notchwidth=0.5)+theme_bw()+
  stat_summary(fun=mean, geom='point', shape=20,colour='red',size=6)+
   facet_wrap(~year,nrow=2)

##timeseries plot for bihar
library(readxl)
data <- read_excel("Bihar_ts_plot.xlsx")
View(data)
date = as.POSIXct('2001-01-01')
date = seq.POSIXt(date, by='month', length.out = 252)
data$date = date     
data$year = as.numeric(format(data$date,'%Y'))
data$year = as.factor(data$year)
data = data %>% select(-1)
data_old = data[1:228,]
data_new = data[229:252,]
data_old_final = data_old %>% group_by(year) %>% summarise_if(is.numeric,funs(mean(.,na.rm=T)))
data_old_final = data_old_final[ ,c(2:10,1)]
data_new = data_new %>% select(-10)
data_final =rbind(data_old_final,data_new)
data$Forecast_year =2020
data$date = as.Date(data$date, format = '%Y-%m-%d')
ggplot(data=data)+geom_line(data = data, aes(x=date, y=original), color='darkblue',size=1.05, alpha=0.7)+theme_bw()+
   geom_line(data = data, aes(x=date,y=`Lo95`), color='red',size=1.05, alpha=0.9,linetype='twodash')+
   geom_line(data = data, aes(x=date,y=`Hi95`), color='red',size=1.05, alpha=0.9,linetype='twodash')+
  geom_ribbon(data=data,aes(x=date, y=Forecast, ymin =`Lo95`,ymax=`Hi95`), fill='#b392ac', alpha=0.4)+
  geom_line(data = data, aes(x=date, y=Forecast), color='#d90429', size=1.05, alpha=0.9)+
  geom_point(data = data, aes(x=date, y=original), color='darkblue',size=2.2, shape=19)+
  geom_point(data = data, aes(x=date, y=Forecast), color='#d90429',size=2.2, shape=19)+
  geom_vline(xintercept =as.Date(as.Date("2020-01-01")),color = "#240046",lwd = 1.25, linetype='solid')+
  scale_x_date(date_breaks = "2 year", date_minor_breaks = "1 year", date_labels = '%Y')+
  scale_y_continuous(limits = c(0.2,1.3),breaks = seq(0.2,1.3,0.2),labels= seq(0.2,1.3,0.2))+
  ylab(expression(bold(AOD [~0.55~mu*m])))+ xlab('year')+
  theme(axis.text.x = element_text(colour = 'black', face='bold',size=20,angle=0, vjust=0.3),
        axis.text.y= element_text(colour = 'black', face='bold',size=20), axis.title.y = element_text(colour = 'black', face='bold',size=22),
        axis.title.x = element_text(colour = 'black', face='bold',size=22,vjust=-0.2), panel.background = element_blank(),panel.border = element_rect(colour = "black",fill=NA),
        axis.ticks = element_line(colour = 'black',size=1.05), axis.ticks.length = unit(.4, "cm"))
  
  
##Trendfree mann kendall
library(readxl)
bihar <- read_excel("G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_facets_savgol_updated/stat_individual_raster/bihar_state_stat.xlsx")
View(bihar)
date = as.POSIXct('2001-01-01')
date=seq.POSIXt(date,by='month',length.out = 228)  
bihar$date = date
bihar$date = ymd(bihar$date)
bihar = bihar %>% separate(`month-year`, into=c('month','year'),remove=T, sep="-")
bihar$season = ifelse(bihar$month %in% c("Jan" ,"Feb"),'winter', ifelse(bihar$month %in% c("Mar","Apr","May"),'pre-monsoon',
                ifelse(bihar$month %in% c("June","July","Aug", "Sept"),'monsoon','post-monsoon')))

ggplot(data=bihar, aes(x=date,y=mean))+geom_point(size=2, shape=19)+geom_line(color='#14213d', size=1.05)+
  scale_x_date(date_breaks = "2 year", date_minor_breaks = "1 year", date_labels = '%Y')+ theme()+
geom_smooth(method='lm',lwd = 1.25, color='red', linetype='twodash',fill='#b392ac', alpha=0.7)+
  ylab(expression(bold(AOD [~0.55~mu*m])))+xlab('Year')+
  theme(axis.text.x = element_text(colour = 'black', face='bold',size=20,angle=0, vjust=0.3),
        axis.text.y= element_text(colour = 'black', face='bold',size=20), axis.title.y = element_text(colour = 'black', face='bold',size=22),
        axis.title.x = element_text(colour = 'black', face='bold',size=22,vjust=-1.0), panel.background = element_blank(),panel.border = element_rect(colour = "black",fill=NA),
        axis.ticks = element_line(colour = 'black',size=1.05), axis.ticks.length = unit(.4, "cm"))


##Theilsens slope
library(openair)
library(readxl)
data <- read_excel("bihar_state_stat.xlsx")
View(data)
date = as.POSIXct('2001-01-01')
date = seq.POSIXt(date, by='month', length.out=228)
data$date = date
data$month = as.numeric(format(data$date, '%m'))

data$season = ifelse(data$month %in% c(1:2),'winter',ifelse(data$month %in% c(3:5),'premonsoon',ifelse(data$month %in% c(6:9),'monsoon','postmonsoon')))
data$season = as.factor(data$season)
season = levels(data$season)
bihar_state = lapply(season, function(i){
  k=TheilSen(data %>% filter(season==i) , pollutant='mean', deseason=F, date.format = "%Y", shade='transparent',dec.place=4, lab.cex=1, data.col = '#14213d', ylab='AOD', lwd=2, lty =1, pch=19, autocorr=T, avg.time='year')
  dat_new = k$data[2]
  bihar_state = data.frame(matrix())
  bihar_state[2] = dat_new$res2[1]
  bihar_state[3] = dat_new$res2[2]
  bihar_state[4]= dat_new$res2[11]
  bihar_state[5]= dat_new$res2[12]
  bihar_state[6]= dat_new$res2[16]
  bihar_state[7]= dat_new$res2[17]
  bihar_state[8]= dat_new$res2[18]
  bihar_state$season=i
  bihar_state$dist = 'Bihar'
  bihar_state
})
bihar_state = do.call('rbind.data.frame',bihar_state)

data = list.files(pattern='*.xlsx')
data=data[-39]
data = lapply(data,function(i){
  k = read_excel(i)
  k
})
data = do.call('rbind.data.frame',data)
data$month = str_sub(data$month, start=1, end=3)
data$month = factor(data$month, levels=month.abb)
data$year = as.factor(data$year)
data = data %>% arrange(year,DISTRICT,month)
data$DISTRICT = as.factor(data$DISTRICT)
district_name = as.character(unique(data$DISTRICT))

data$season = ifelse(data$month %in% c('Jan','Feb'),'winter',ifelse(data$month %in% c('Mar','Apr','May'),'premonsoon',ifelse(data$month %in% c('Jun','Jul','Aug','Sep'),'monsoon','postmonsoon')))

state = lapply(district_name, function(i){
  data = data %>% filter(DISTRICT==i)
  data$date = date
  season_dat = lapply(season, function(j){
  k=TheilSen(data %>% filter(season==j), pollutant='mean', deseason=F, date.format = "%Y", shade='transparent',dec.place=4, lab.cex=1, data.col = '#14213d', ylab='AOD', avg.time='year')
  dat_new = k$data[2]
  bihar_state = data.frame(matrix())
  bihar_state[2] = dat_new$res2[1]
  bihar_state[3] = dat_new$res2[2]
  bihar_state[4]= dat_new$res2[11]
  bihar_state[5]= dat_new$res2[12]
  bihar_state[6]= dat_new$res2[16]
  bihar_state[7]= dat_new$res2[17]
  bihar_state[8]= dat_new$res2[18]
  bihar_state$season=j
  bihar_state$dist = i
  bihar_state
})
  bihar_state = do.call('rbind.data.frame',season_dat)
  bihar_state
})

state = do.call('rbind.data.frame',state)
state = rbind(state,bihar_state)
state$dist = str_to_title(state$dist)
state = state %>% select(-c(1,2))

write.table(state, file = 'G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_facets_savgol_updated/mk_openair_seasonal.csv', row.names = F, sep=",")
