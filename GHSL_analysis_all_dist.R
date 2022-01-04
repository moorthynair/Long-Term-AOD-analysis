##To anlyse the change in Global Human Settlement and AOD for entire districts in the state for the year 2015 over 2001

fil_stack = list.files(pattern='*.xlsx')

fil_stack =lapply(fil_stack, function (i){
  file_read = read_excel(i)
  file_read$dist=i
  file_read= file_read %>% tidyr::separate(dist,sep="\\.", into=c("dist",'type'), remove = T)
  file_read
})
comb = do.call('rbind.data.frame', fil_stack)
comb[,c(1,3,6)]=lapply(comb[,c(1,3,6)], factor)
comb=comb[,1:6]

comb$category =ifelse((comb$`GHSL-2001`==comb$`GHSL-2015`),'No change', 
                       ifelse((comb$`GHSL-2001`==10)&(comb$`GHSL-2015` %in% levels(comb$`GHSL-2015`)),'Water Area (WA)',
                              ifelse((comb$`GHSL-2001`==11)&(comb$`GHSL-2015` %in% levels(comb$`GHSL-2015`)),'Very Low Density Rural Area (VLDRA)',
                                     ifelse((comb$`GHSL-2001`==12)&(comb$`GHSL-2015` %in% levels(comb$`GHSL-2015`)),'Low Density Rural Area (LDRA)',                                                                                                                                    
                                            ifelse((comb$`GHSL-2001`==13)&(comb$`GHSL-2015` %in% levels(comb$`GHSL-2015`)),'Rural Cluster (RC)',
                                                   ifelse((comb$`GHSL-2001`==21)&(comb$`GHSL-2015` %in% levels(comb$`GHSL-2015`)),'Suburban (SUB)',
                                                          ifelse((comb$`GHSL-2001`==22)&(comb$`GHSL-2015` %in% levels(comb$`GHSL-2015`)),'Semi Dense Urban Cluster (SDUC)',
                                                                 ifelse((comb$`GHSL-2001`==23)&(comb$`GHSL-2015` %in% levels(comb$`GHSL-2015`)),'Dense Urban Cluster (DUC)','Urban Cluster (UC)'))))))))
comb_final = comb %>% mutate_at(vars('GHSL-2015','GHSL-2001'), funs(recode(.,`10`='WA',`11`='VLDRA',`12`='LDRA',`13`='RC',`21`='SUB',`22`='SDUC',
                                                                       `23`='DUC',`30`='UC')))

comb_final$percent = round(((comb_final$`AOD-2015`-comb_final$`AOD-2001`)*100/comb_final$`AOD-2001`), digits=1)
comb_final$category=factor(comb_final$category,levels=c('Urban Cluster (UC)','Dense Urban Cluster (DUC)','Semi Dense Urban Cluster (SDUC)','Suburban (SUB)','Rural Cluster (RC)','Low Density Rural Area (LDRA)','Very Low Density Rural Area (VLDRA)','Water Area (WA)','No change'))
comb_final$`GHSL-2015`=factor(comb_final$`GHSL-2015`, levels=c('UC','DUC','SDUC','SUB','RC','LDRA','VLDRA','WA'))
comb_final$`GHSL-2001`=factor(comb_final$`GHSL-2001`, levels=c('UC','DUC','SDUC','SUB','RC','LDRA','VLDRA','WA'))
comb_final=na.omit(comb_final)
write.table(comb_final %>% filter(category=='No change'), file='comphrensive_dist_year_GMOD.csv', row.names = F, sep=",")
k =comb_final %>%  filter(category=='No change' ) %>% group_by(dist) %>% filter(category=='UC')

dist_name =levels(comb_final$dist)
dist_name=c("BANKA","JAMUI","PATNA") ##Enter the districts in the state
lapply(dist_name, function(i){
  bihar_final=comb_final %>% filter(dist==i)
 ggplot(data=bihar_final, aes(x=`GHSL-2015`, y=percent))+geom_bar(stat='identity',fill="steelblue4", col='black', alpha=0.8)+ theme_bw()+ 
    labs(x='Settlement-2015', y='Percentage change (%)')+ ggtitle (i)+
    theme(axis.text.x = element_text(face='bold',color='black',size=9,angle = 90, vjust=0.5),strip.text.x = element_text(face="bold", size=10,color="black"), axis.text.y = element_text(face='bold',color='black',size=9),
          axis.title = element_text(face='bold',color='black',size=10),panel.background = element_blank(),panel.border = element_rect(colour = "black",fill=NA),strip.background = element_rect(colour="black", fill='grey94'), plot.title = element_text(face='bold',color='black',size=12, hjust=0.5))+scale_y_continuous(limits = c(0,80), breaks = seq(0,80,20), labels = seq(0,80,20))+ geom_text(aes(label=paste(" ",percent,'%',sep="", paste("",sep ='\n',paste("(",count,")",sep="")))), vjust=-0.1, hjust=0.5,size=3.1, fontface=2)+ 
    facet_wrap(~category)
 path_name ="C:/Users/HP/Desktop/Satellite-Data-Analysis/Processed_raster/Raster_facets_savgol_updated/G_MOD/"
 img_name =paste(path_name,i,'.png',sep="")
 ggsave(img_name, height= 18, width=28, units='cm',dpi=300)
 q =paste(i, 'is saved', sep="")
 print(q)
})

