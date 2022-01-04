#To understand the monthly variation in AOD over various Global Human Settlements in the districts for the State. 

fil_stack = list.files(pattern='*.xlsx')

fil_stack =lapply(fil_stack, function (i){
  file_read = read_excel(i)
  file_read$dist=i
  file_read= file_read %>% tidyr::separate(dist,sep="\\.", into=c('dist','type'), remove = T)
  file_read = file_read %>% rename('GHSL_2015'=1, 'AOD_2015'=2,'GHSL_2001'=3, 'AOD_2001'=4)
  file_read
})
comb = do.call('rbind.data.frame', fil_stack)
comb =comb %>% separate(dist, sep="-", into =c('dist','x'), remove=T)
comb[,c(1,3,5,6)]=lapply(comb[,c(1,3,5,6)], factor)
comb=comb[,1:6]
comb_final = comb %>% mutate_at(vars('GHSL_2015','GHSL_2001'), funs(recode(.,`10`='WA',`11`='VLDRA',`12`='LDRA',`13`='RC',`21`='SUB',`22`='SDUC',
                      `23`='DUC',`30`='UC')))
new_val =comb_final %>% group_by(dist,GHSL_2015) %>% summarise(avg =mean(AOD_2015), count=n())
new_val = new_val %>% group_by(dist) %>% mutate(percent_area = count*100/sum(count))
new_cast = dcast(new_val[,-4], dist~GHSL_2015)

col_max = as.data.frame(colnames(new_cast[,-c(1,2,6)])[apply(new_cast[,-c(1,2,6)],1,which.max)])
combined = cbind(col_max, new_cast[,1])
combined= combined[ ,c(2,1)]
combined= combined %>% rename('dist'=1, 'GHSL_2015'=2)
comb_together = merge(combined, new_val, by = c( "dist","GHSL_2015"))

new_val1 =comb_together %>% mutate_at(vars('GHSL_2015'), funs(recode(.,'VLDRA'='Regional', 'LDRA'= 'Rural', 'RC'='Rural','UC'='Urban','DUC'='Urban')))
write.table(new_val, file='GHSL_dist_classification_2015_2.csv', row.names = F, sep=",")


##segregate the data and generate bar plot for the year 2001 and 2015
comb1 = comb_final %>% select(3,4,5,6)
comb1 =na.omit(comb1)
comb1 = comb1 %>% mutate(GHSL_2001 = recode(GHSL_2001,'WA'='Background', 'VLDRA'='Background','RC'='Rural', 'LDRA'='Rural','SUB'='Urban','SDUC'='Urban','DUC'='Urban','UC'='Urban'))
comb1 = comb1 %>% group_by(dist,GHSL_2001) %>% summarise(mean = mean(AOD_2001))
comb1$dist=as.factor(comb1$dist)


`%notin%` = Negate(`%in%`)
ggplot(data=comb1 %>% filter(dist %notin% c('Bihar','Bihar_2016')), aes(x= GHSL_2001, y=mean, fill = GHSL_2001))+geom_col(position ='dodge', alpha=0.9, col='black')+ theme_bw()+ 
  scale_fill_manual(name=' Class',values = c('#197278','#bb9457','#b23a48'), limits= c('Urban','Rural','Background'))+labs(x = 'District', y='AOD')+ theme(axis.text = element_text(face = 'bold', color='black',size=8), axis.title = element_text(face = 'bold', color='black',size=12),
                                                                                                                  legend.title = element_text(face = 'bold', color='black',size=12), legend.text = element_text(face = 'bold', color='black',size=10),
                                                                                                                  panel.background = element_blank(), panel.grid = element_blank())+facet_wrap(~dist)


comb_new = comb_final 
comb_new =na.omit(comb_new)
comb_new = comb_new %>% mutate_at(vars(GHSL_2015,GHSL_2001),funs(recode(.,'WA'='Background', 'VLDRA'='Background','RC'='Rural', 'LDRA'='Rural','SUB'='Urban','SDUC'='Urban','DUC'='Urban','UC'='Urban')))
comb_2001 = comb_new %>% group_by(dist,month,GHSL_2001) %>% summarise(mean_2001 = mean(AOD_2001))
comb_2015 = comb_new %>% group_by(dist,month,GHSL_2015) %>% summarise(mean_2015 = mean(AOD_2015))
comb_new$dist=as.factor(comb_new$dist)
comb_new = merge(comb_2001, comb_2015, by.x = c('dist','month','GHSL_2001'), by.y = c('dist','month','GHSL_2015'))
comb_new$month =factor(comb_new$month, levels= c("Jan",'Feb','Mar','Apr','May','June','July','Aug','Sept','Oct','Nov','Dec'))
comb_new$GHSL_2001=factor(comb_new$GHSL_2001, levels = c("Urban",'Rural','Background'))
comb_new = comb_new %>% arrange(month)
comb_new_mean = as.data.frame(cbind(comb_new[,1:3],paste(round(comb_new$mean_2001,digits=3)," (",round(comb_new$mean_2015,digits=3),")",sep="")))
comb_bihar = comb_new %>% group_by(month,GHSL_2001) %>% summarise_at(vars(mean_2001, mean_2015),funs(mean))
comb_bihar = as.data.frame(cbind(comb_bihar[,1:2],paste(round(comb_bihar$mean_2001,digits=3)," (",round(comb_bihar$mean_2015,digits=3),")",sep="")))
comb_bihar = comb_bihar %>% arrange(month)
write.table(comb_bihar, file= 'combined_bihar_month.csv', row.names=F, sep=",")
comb_bihar = comb_bihar %>% separate(val2, sep='//()// ', into=c('val2','val3'), remove=T)
ggplot(comb_bihar, aes(month,val1, color =GHSL_2001, group=1))+geom_point(aes(size=val1))
