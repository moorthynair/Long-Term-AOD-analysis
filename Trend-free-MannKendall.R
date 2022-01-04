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
