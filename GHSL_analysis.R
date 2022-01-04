##To analyse the change in Global Human Settlement and AOD in the state for the year 2015 over 2001

library(readxl)
bihar <- read_excel("Bihar.xlsx")
View(bihar)
bihar[,c(1,3)]=lapply(bihar[,c(1,3)],factor)
bihar %>% filter(`GHSL-2015`==23 & `GHSL-2001`==13) %>% 
  summarise(count=n(), avg_2015=mean(`AOD-2015`),avg_2001=mean(`AOD-2001`))         
library(dplyr)
bihar$category =ifelse((bihar$`GHSL-2001`==bihar$`GHSL-2015`),'No change', 
                       ifelse((bihar$`GHSL-2001`==10)&(bihar$`GHSL-2015` %in% levels(bihar$`GHSL-2015`)),'Water Area (WA)',
                       ifelse((bihar$`GHSL-2001`==11)&(bihar$`GHSL-2015` %in% levels(bihar$`GHSL-2015`)),'Very Low Density Rural Area (VLDRA)',
                       ifelse((bihar$`GHSL-2001`==12)&(bihar$`GHSL-2015` %in% levels(bihar$`GHSL-2015`)),'Low Density Rural Area (LDRA)',                                                                                                                                    
                       ifelse((bihar$`GHSL-2001`==13)&(bihar$`GHSL-2015` %in% levels(bihar$`GHSL-2015`)),'Rural Cluster (RC)',
                       ifelse((bihar$`GHSL-2001`==21)&(bihar$`GHSL-2015` %in% levels(bihar$`GHSL-2015`)),'Suburban (SUB)',
                       ifelse((bihar$`GHSL-2001`==22)&(bihar$`GHSL-2015` %in% levels(bihar$`GHSL-2015`)),'Semi Dense Urban Cluster (SDUC)',
                       ifelse((bihar$`GHSL-2001`==23)&(bihar$`GHSL-2015` %in% levels(bihar$`GHSL-2015`)),'Dense Urban Cluster (DUC)','Urban Cluster (UC)'))))))))
bihar = bihar %>% mutate_at(vars('GHSL-2015','GHSL-2001'), funs(recode(.,`10`='WA',`11`='VLDRA',`12`='LDRA',`13`='RC',`21`='SUB',`22`='SDUC',
                                                                           `23`='DUC',`30`='UC')))
bihar_final =na.omit(bihar)
bihar_final$percent = round(((bihar_final$`AOD-2015`-bihar_final$`AOD-2001`)*100/bihar_final$`AOD-2001`), digits=1)
bihar_final$category=factor(bihar_final$category,levels=c('Urban Cluster (UC)','Dense Urban Cluster (DUC)','Semi Dense Urban Cluster (SDUC)','Suburban (SUB)','Rural Cluster (RC)','Low Density Rural Area (LDRA)','Very Low Density Rural Area (VLDRA)','Water Area (WA)','No change'))
bihar_final$`GHSL-2015`=factor(bihar_final$`GHSL-2015`, levels=c('UC','DUC','SDUC','SUB','RC','LDRA','VLDRA','WA'))
bihar_final$`GHSL-2001`=factor(bihar_final$`GHSL-2001`, levels=c('UC','DUC','SDUC','SUB','RC','LDRA','VLDRA','WA'))

bihar_segg = bihar_final %>% filter(count>=mean(count))
library(ggplot2)
ggplot(data=bihar_final, aes(x=`GHSL-2015`, y=percent))+geom_bar(stat='identity',fill="steelblue4", col='black', alpha=0.8)+ theme_bw()+ 
  labs(x='Settlement-2015', y='Percentage change (%)')+
  theme(axis.text.x = element_text(face='bold',color='black',size=16,angle = 90, vjust=0.5),strip.text.x = element_text(face="bold", size=14,color="black"), axis.text.y = element_text(face='bold',color='black',size=16),
        axis.title = element_text(face='bold',color='black',size=18),panel.background = element_blank(),panel.border = element_rect(colour = "black",fill=NA),strip.background = element_rect(colour="black", fill='grey94'),
        axis.title.x = element_text(vjust=-1.0),axis.title.y = element_text(vjust=2.0))+scale_y_continuous(limits = c(0,80), breaks = seq(0,80,20), labels = seq(0,80,20))+ geom_text(aes(label=paste(" ",percent,'%',sep="", paste("",sep ='\n',paste("(",count,")",sep="")))), vjust=-0.1, hjust=0.5,size=4.5, fontface=2)+ 
  facet_wrap(~category)

aod_2001 =bihar_final %>% group_by(`GHSL-2001`) %>% summarise(mean=mean(`AOD-2001`))
aod_2015 =bihar_final %>% group_by(`GHSL-2015`) %>% summarise(mean=mean(`AOD-2015`))

comb = merge(aod_2001,aod_2015, by.x = 'GHSL-2001', by.y='GHSL-2015')
comb=comb %>% rename('aod_2001'=2,'aod_2015'=3) %>% mutate(change= (aod_2015-aod_2001)/(aod_2001))
