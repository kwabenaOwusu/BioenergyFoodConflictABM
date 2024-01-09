#----------------------------------------------------------------------------
# Sensitivity analysis code 
# By: Kwabena Afriyie, Owusu
# Created: 05.01.2024
#----------------------------------------------------------------------------
library(ggplot2)
library(dplyr)
library(tidyr)
library(egg)
library(grid)
library(gridExtra)
library(ggpubr)
library(scales)
library(latex2exp)

library(multcomp)
library(nlme)
library(car)
library(pastecs)
library(reshape)
library(WRS2)
library(ez) 
library(compute.es)
library(stringr) # remove space on characters

##--------------------------------------------------------------------------------------------------
## parameters for sensitivity ##
setwd("/Users/kwabx/labspaces/bioenergy_landuse_conflict_model/data/work/") # set working directory

lstfile<-c("yield_food_1.2.csv","yield_food_3.6.csv",
           "yield_bioenergy_1.76.csv","yield_bioenergy_5.23.csv",
           "cost_food_1208.csv","cost_food_3624.csv",
           "cost_bioenergy_1466.csv","cost_bioenergy_4399.csv",
           "total_demand_food_560000000.0.csv","total_demand_food_1670000000.0.csv",
           "total_demand_bioenergy_16000000.0.csv","total_demand_bioenergy_48000000.0.csv")

## columns in the csv file ##
timdat<-data.frame(time=c(), price_bioenergy=c(), price_food=c(), harvest_bioenergy=c(),
                    harvest_food=c(), land_fertility=c(), priority_food=c(), priority_bioenergy=c(),
                    priority_fallow=c(),land_food=c(), land_bioenergy=c(),capital=c(), food_direction=c(),
                    bioenergy_direction=c(), no_interaction=c(), yes_interaction=c(), treatments=c(), NoSim=c(),
                    treatment=c(), parameter=c(), change=c(), crop=c())

#combining all the data of interest ### 
for(fi in lstfile){
  infile<-read.table(fi, sep=',', header=T)
  infile<-data.frame(infile)  # each of length 4 time steps
  ttpp<-data.frame(time=infile$time,
                   price_bioenergy = infile$price_bioenergy,
                   price_food = infile$price_food,
                   harvest_bioenergy = infile$harvest_bioenergy,
                   harvest_food = infile$harvest_food,
                   land_fertility = infile$land_fertility,
                   priority_food = infile$priority_food,
                   priority_bioenergy = infile$priority_bioenergy,
                   priority_fallow = infile$priority_fallow,
                   land_food= infile$land_food,
                   land_bioenergy= infile$land_bioenergy,
                   capital= infile$capital,
                   food_direction= infile$food_direction,
                   bioenergy_direction= infile$bioenergy_direction,
                   no_interaction=infile$no_interaction,
                   yes_interaction=infile$yes_interaction,
                   treatments =infile$treatments,
                   NoSim = infile$NoSim,
                   treatment = infile$treatment,
                   parameter = infile$parameter,
                   change = infile$change,
                   crop = infile$crop)
  timdat<-rbind(timdat, ttpp)
}


## nexted data as required ##
bxpdat_mean <- timdat  %>% group_by(parameter,crop,treatment,change,NoSim) %>% summarise(N=n(), 
                                                                                         price_bioenergy = mean(price_bioenergy,na.rm=T),
                                                                                         price_food = mean(price_food,na.rm=T),
                                                                                         harvest_bioenergy = mean(harvest_bioenergy,na.rm=T),
                                                                                         harvest_food = mean(harvest_food,na.rm=T),
                                                                                         land_fertility = mean(land_fertility,na.rm=T),
                                                                                         priority_food = mean(priority_food, na.rm=T),
                                                                                         priority_bioenergy = mean(priority_bioenergy, na.rm=T),
                                                                                         priority_fallow = mean(priority_fallow, na.rm = T),
                                                                                         land_food = mean(land_food, na.rm = T),
                                                                                         land_bioenergy = mean(land_bioenergy, na.rm = T)) 


long_bxpdat_mean <- bxpdat_mean %>% gather(variables, mean_values, harvest_bioenergy, harvest_food) # change from wide to long format 
long_bxpdat_mean$variables <- as.factor(as.vector(long_bxpdat_mean$variables)) # x-axis treated as continuous variable
long_bxpdat_mean$treatment<- as.factor(long_bxpdat_mean$treatment) 
long_bxpdat_mean$parameter<- as.factor(long_bxpdat_mean$parameter)
long_bxpdat_mean$change<- as.factor(long_bxpdat_mean$change) 
long_bxpdat_mean$crop<- as.factor(long_bxpdat_mean$crop) 
long_bxpdat_mean$mean_values <- long_bxpdat_mean$mean_values / 1000

## add another column called sesitivity with values according to sensitivity index ##
long_bxpdat_mean <- long_bxpdat_mean %>%  mutate(sensitivity = case_when(variables == "harvest_food" ~ ((mean_values - 374.547) / 374.547) * 100, 
                                                                         variables == "harvest_bioenergy" ~ ((mean_values - 70.8562) / 70.8562) * 100 ))


lablist=as.vector(c(
  expression(bold(c^bioenergy)),expression(bold(c^food)),
  expression(bold(D^bioenergy)),expression(bold(D^food)),
  expression(bold(B^bioenergy)),expression(bold(B^food))
))  # the x-axis showing symbols of parameters


# filter only that corresponding to harvest food
HARVEST_FOOD <- long_bxpdat_mean %>% filter(variables == 'harvest_food')  %>% group_by(parameter,crop,treatment,change) %>% summarise(N=n(),sensitivity = mean(sensitivity,na.rm=T))
lcols<-c("#677CB9","#60C171") #ligther color scale
gplt1<-ggplot(HARVEST_FOOD, aes(x=parameter, y= sensitivity, fill= change)) + geom_bar(stat="identity", width=0.5 ,position=position_dodge()) + 
  geom_hline(yintercept=0, size=0.8) +  labs(x=NULL, y='Change in food harvest (%)') + 
  scale_fill_manual(values=lcols, labels = c('-50% standard', '+50% standard'), name = 'Change in parameter') +
  scale_y_continuous(limits=c(-100,100),breaks=seq(-100,100,10),sec.axis=sec_axis(~.*1,labels=NULL,breaks = seq(-100,100, by = 10))) +
  scale_x_discrete(expand=c(0.15,0.15), labels=lablist, guide = guide_axis(angle = 0)) + 
  theme_linedraw() +
  theme(text=element_text(size=16), title=element_text(face='bold'), axis.ticks=element_line(size=0.75), axis.ticks.length=unit(-.3,'cm'), axis.title.y=element_text(vjust=-1),axis.text.x = element_text(vjust=0,size=15, margin=unit(rep(0.30,4),'cm')) ,axis.text.y=element_text(size=13, margin=unit(rep(0.30,4),'cm')),  panel.grid.minor=element_blank(), panel.grid.major=element_line(colour = "grey70", size = 0.2), panel.background=element_rect(colour="black",size=4), plot.margin=unit(c(0.5,0.5,0.5,0.25),'cm'), legend.key=element_blank(), legend.position=c(0.5,0.85), legend.direction='vertical', legend.title.align=0, legend.background=element_rect(fill=NA), legend.box.background=element_rect(fill='white', size=0.5), legend.box='horizontal', legend.key.size=unit(0.5, 'cm'), legend.title=element_text(size=12), legend.text=element_text(size=12), legend.spacing.y=unit(0.2, 'cm'), legend.spacing.x=unit(0.02, 'cm') )
gplt1



# filter only that corresponding to harvest bioenergy
HARVEST_BIOENERGY <- long_bxpdat_mean %>% filter(variables == 'harvest_bioenergy') %>% group_by(parameter,crop,treatment,change) %>% summarise(N=n(),sensitivity = mean(sensitivity,na.rm=T))
lcols<-c("#677CB9","#60C171") #ligther color scale
gplt2<-ggplot(HARVEST_BIOENERGY, aes(x=parameter, y= sensitivity, fill= change)) + geom_bar(stat="identity", width=0.5 ,position=position_dodge()) + 
  geom_hline(yintercept=0, size=0.8) +  labs(x=NULL, y='Change in bioenergy harvest (%)') + 
  scale_fill_manual(values=lcols, labels = c('-50% standard', '+50% standard'), name = 'Change in parameter') +
  scale_y_continuous(limits=c(-100,100),breaks=seq(-100,100,10),sec.axis=sec_axis(~.*1,labels=NULL,breaks = seq(-100,100, by = 10))) +
  scale_x_discrete(expand=c(0.15,0.15), labels=lablist, guide = guide_axis(angle = 0)) + 
  theme_linedraw() +
  guides(colour='none', fill='none', linetype='none', alpha='none' ) +
  theme(text=element_text(size=16), title=element_text(face='bold'), axis.ticks=element_line(size=0.75), axis.ticks.length=unit(-.3,'cm'), axis.title.y=element_text(vjust=-1),axis.text.x = element_text(vjust=0,size=15, margin=unit(rep(0.30,4),'cm')) ,axis.text.y=element_text(size=13, margin=unit(rep(0.30,4),'cm')),  panel.grid.minor=element_blank(), panel.grid.major=element_line(colour = "grey70", size = 0.2), panel.background=element_rect(colour="black",size=4), plot.margin=unit(c(0.25,0.5,1.1,0.25),'cm'), legend.key=element_blank(), legend.position=c(0.8,0.9), legend.direction='vertical', legend.title.align=0, legend.background=element_rect(fill=NA), legend.box.background=element_rect(fill='white', size=0.5), legend.box='horizontal', legend.key.size=unit(0.5, 'cm'), legend.title=element_text(size=12), legend.text=element_text(size=12), legend.spacing.y=unit(0.2, 'cm'), legend.spacing.x=unit(0.02, 'cm') )
gplt2



### Combine plots 
quartz(file= '/Users/kwabx/labspaces/bioenergy_landuse_conflict_model/data/work/sensitivity.pdf', type='pdf', dpi=2500, width=10, height=9, bg="white")
figure_sensitivity=ggarrange(
  gplt1,
  gplt2,
  nrow = 2, ncol = 1, align = "v", widths = c(1,1),
  labels = 'AUTO', font.label = list(size = 20, color = "black"),
  vjust = c(2.5,2.5), hjust = c(-6,-6) )
figure_sensitivity
graphics.off()


