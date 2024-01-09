#----------------------------------------------------------------------------
# Experiments code 
# By: Kwabena Afriyie, Owusu
# Created: 02.01.2024
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
## reading the data
lstfile<-c("/Users/kwabx/labspaces/bioenergy_landuse_conflict_model/data/work/experiments_simulation3.csv",
           "/Users/kwabx/labspaces/bioenergy_landuse_conflict_model/data/work/experiments_simulation4.csv")

timdat<-data.frame( time=c(), price_bioenergy=c(), price_food=c(), harvest_bioenergy=c(),
                    harvest_food=c(), land_fertility=c(), priority_food=c(), priority_bioenergy=c(),
                    priority_fallow=c(),land_food=c(), land_bioenergy=c(),capital=c(), food_direction=c(),
                    bioenergy_direction=c(), no_interaction=c(), yes_interaction=c(), treatment=c(), NoSim=c())

for(fi in lstfile){
  infile<-read.table(fi, sep=',' ,header=T)
  infile<-data.frame(infile)  
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
                   treatment =infile$treatment,
                   NoSim = infile$NoSim)
  timdat<-rbind(timdat, ttpp)
}


##--------------------------------------------------------------------------------------------------
## timeplot of harvest
timdat_mean <- timdat %>%  filter(time <=25) %>% group_by(treatment,time) %>% summarise(N=n(), 
                                                       price_bioenergy = mean(price_bioenergy,na.rm=T),
                                                         price_food = mean(price_food,na.rm=T),
                                                         harvest_bioenergy = mean(harvest_bioenergy,na.rm=T),
                                                         harvest_food = mean(harvest_food,na.rm=T),
                                                         land_fertility = mean(land_fertility,na.rm=T),
                                                         priority_food = mean(priority_food, na.rm=T),
                                                         priority_bioenergy = mean(priority_bioenergy, na.rm=T),
                                                         priority_fallow = mean(priority_fallow, na.rm = T),
                                                         land_food = mean(land_food, na.rm = T),
                                                         land_bioenergy = mean(land_bioenergy, na.rm = T) ,
                                                         capital = mean(capital, na.rm = T))

long_timdat <- timdat_mean %>% gather(variables, mean_values, harvest_food, harvest_bioenergy) # change from wide to long format
long_timdat$time <- as.numeric(as.vector(long_timdat$time)) # x-axis treated as continuous variable
long_timdat$treatment<- as.factor(long_timdat$treatment) # treatment treated as factor variable
long_timdat$mean_values <- long_timdat$mean_values / 1000

long_timdat_food = long_timdat %>% filter(variables == "harvest_food")
long_timdat_bioenergy = long_timdat %>% filter(variables == "harvest_bioenergy")
  

plt1=ggplot(data=long_timdat_food, aes(x=time, y=mean_values, group=interaction(treatment,variables),linetype=treatment, color=variables)) +  geom_line(size=1,color='royalblue') + 
  labs(x=NULL, y=TeX(r"(\textbf{Food harvest ${(x \; 10^3 \; tons)}}$)")) +
  scale_x_continuous(limits=c(0,25), breaks = seq(0, 25, by = 5), expand=c(0.005,0.005), sec.axis=sec_axis(~.*1,labels=NULL,breaks = seq(0, 25, by = 5))) + 
  scale_y_continuous(limits=c(0,600),breaks = seq(0, 600, by = 100),expand=c(0.005,0.005), sec.axis=sec_axis(~.*1,labels=NULL,breaks = seq(0, 600, by = 100))) +
  scale_linetype_manual(values=c("solid", "dashed"), name = "Treatment", labels = c('Interaction', 'No interaction'))  +
  theme_linedraw() +
  #guides(colour='none', fill='none', linetype='none', alpha='none' ) +
  # geom_vline(xintercept=25, linetype="solid", color = "black", size=0.5) +
  # annotate("text", x=25, y=580, label="no interaction", angle=0, size=6, color="black") +
  # scale_size_manual(values = NULL,labels = NULL, name=NULL,guide = FALSE) +
  #scale_color_discrete(name = "Harvest", labels = c('Bioenergy crop', 'Food crop')) +
  #guides(colour='none', fill=guide_legend(direction='horizontal', title.position='top', label.position='right'), linetype='none', alpha=guide_legend(direction='horizontal', title.position='top', label.position='right', override.aes=list(fill=c(alpha('grey', 0.0), alpha('grey', 0.8))) ) ) +
  theme(text=element_text(size=16), plot.title = element_text(hjust=0.5,vjust=3,color="black", size=18, face="bold.italic"), title=element_text(face='bold'), axis.ticks=element_line(size=0.75), axis.ticks.length=unit(-0.3,'cm'), axis.title.y=element_text(vjust=-1), axis.title.y.right = element_text(vjust=-1,color = 'black'), axis.text.x = element_text(vjust = -1, size=15, margin=unit(rep(0.30,4),'cm')), axis.text.y=element_text(size=15, margin=unit(rep(0.30,4),'cm')), axis.text.y.right=element_text(size=15, margin=unit(rep(0.30,4),'cm')), panel.grid.minor=element_blank(), panel.grid.major=element_blank(), panel.background=element_rect(colour="black",size=4), plot.margin=unit(c(0.5,0.6,0.5,0.25),'cm'), legend.key=element_blank(), legend.position=c(0.2,0.2), legend.direction="vertical", legend.title.align=0, legend.background=element_rect(fill=NA), legend.box.background=element_rect(fill='white', size=0.5), legend.box='vertical', legend.key.size=unit(0.8, 'cm'),legend.title=element_text(size=16), legend.text=element_text(size=14), legend.spacing.y=unit(0.02, 'cm'), legend.spacing.x=unit(0.01, 'cm') )
plt1


plt2=ggplot(data=long_timdat_bioenergy, aes(x=time, y=mean_values, group=interaction(treatment,variables),linetype=treatment, color=variables)) +  geom_line(size=1,color='mediumseagreen') + 
  labs(x=TeX(r"(\textbf{Time (year)})"), y=TeX(r"(\textbf{Bioenergy harvest ${(x \; 10^3 \; tons)}}$)")) +
  scale_x_continuous(limits=c(0,25), breaks = seq(0, 25, by = 5), expand=c(0.005,0.005), sec.axis=sec_axis(~.*1,labels=NULL,breaks = seq(0, 25, by = 5))) + 
  scale_y_continuous(limits=c(0,80),breaks = seq(0, 80, by = 20),expand=c(0.005,0.005), sec.axis=sec_axis(~.*1,labels=NULL,breaks = seq(0, 80, by = 20))) +
  #scale_fill_manual(values=lcols, labels = c('Jatropha', 'Maize'), name = 'Type of crop') +
  scale_linetype_manual(values=c("solid", "dashed"), name = "Treatment", labels = c('Interaction', 'No interaction'))  +
  theme_linedraw() + 
  guides(colour='none', fill='none', linetype='none', alpha='none' ) +
  theme(text=element_text(size=16), plot.title = element_text(hjust=0.5,vjust=3,color="black", size=18, face="bold.italic"), title=element_text(face='bold'), axis.ticks=element_line(size=0.75), axis.ticks.length=unit(-0.3,'cm'), axis.title.y=element_text(vjust=-1), axis.title.y.right = element_text(vjust=-1,color = 'black'), axis.text.x = element_text(vjust = -1, size=15, margin=unit(rep(0.30,4),'cm')), axis.text.y=element_text(size=15, margin=unit(rep(0.30,4),'cm')), axis.text.y.right=element_text(size=15, margin=unit(rep(0.30,4),'cm')), panel.grid.minor=element_blank(), panel.grid.major=element_blank(), panel.background=element_rect(colour="black",size=4), plot.margin=unit(c(0.25,0.6,1.1,0.25),'cm'), legend.key=element_blank(), legend.position=c(0.5,0.9), legend.direction="vertical", legend.title.align=0, legend.background=element_rect(fill=NA), legend.box.background=element_rect(fill='white', size=0.5), legend.box='vertical', legend.key.size=unit(0.8, 'cm'),legend.title=element_text(size=16), legend.text=element_text(size=14), legend.spacing.y=unit(0.02, 'cm'), legend.spacing.x=unit(0.01, 'cm') )
plt2


##--------------------------------------------------------------------------------------------------
## bxplt of harvest
bxpdat <- timdat  %>% group_by(treatment,NoSim) %>% summarise(N=n(), 
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

long_bxpdat <- bxpdat %>% gather(variables, mean_values, harvest_bioenergy, harvest_food) # change from wide to long format
long_bxpdat$variables <- as.factor(as.vector(long_bxpdat$variables)) # x-axis treated as continuous variable
long_bxpdat$treatment<- as.factor(long_bxpdat$treatment) # treatment treated as factor variable
long_bxpdat$mean_values <- long_bxpdat$mean_values / 1000

long_bxpdat_food = long_bxpdat %>% filter(variables == "harvest_food")
long_bxpdat_bioenergy = long_bxpdat %>% filter(variables == "harvest_bioenergy")

lcols<-c("blue","red") # color
bxp1=ggplot(data=long_bxpdat_food, aes(x=variables, y=mean_values, group=interaction(treatment,variables), fill = NULL, linetype= treatment )) +  geom_boxplot(width=0.3) + 
  labs(x=NULL, y=NULL)  +   
  scale_x_discrete(expand=c(0.005,0.005),labels = NULL) + 
  scale_y_continuous(limits=c(0,600),breaks = seq(0,600, by = 100),labels = NULL,expand=c(0.005,0.005), sec.axis=sec_axis(~.*1,labels=NULL,breaks = seq(0,600, by = 100))) +
  theme_linedraw() + 
  #scale_fill_manual(values=lcols, labels = c('Jatropha', 'Maize'), name = 'Type of crop') +
  scale_linetype_manual(values=c("solid", "dashed"), name = "Treatment", labels = c('Interaction', 'No interaction'))  +
  #theme(text=element_text(size=16), title=element_text(face='bold'), axis.ticks=element_line(size=0.75), axis.ticks.length=unit(-.3,'cm'), axis.title.y=element_text(vjust=-1),axis.text.x = element_blank() ,axis.text.y=element_text(size=13, margin=unit(rep(0.30,4),'cm')),  panel.grid.minor=element_blank(), panel.grid.major=element_blank(), panel.background=element_rect(colour="black",size=4), plot.margin=unit(c(0.5,0.5,1.1,0.6),'cm'), legend.key=element_blank(), legend.position=c(0.2,0.2), legend.direction='vertical', legend.title.align=0, legend.background=element_rect(fill=NA), legend.box.background=element_rect(fill='white', size=0.5), legend.box='vertical', legend.key.size=unit(0.45, 'cm'), legend.title=element_text(size=11), legend.text=element_text(size=11), legend.spacing.y=unit(0.01, 'cm'), legend.spacing.x=unit(0.01, 'cm') )
  theme(text=element_text(size=16), plot.title = element_text(hjust=0.5,vjust=3,color="black", size=18, face="bold.italic"), title=element_text(face='bold'), axis.ticks=element_line(size=0.75), axis.ticks.length=unit(-0.3,'cm'), axis.title.y=element_text(vjust=-1), axis.title.y.right = element_text(vjust=-1,color = 'black'), axis.text.x = element_text(vjust = -1, size=15, margin=unit(rep(0.30,4),'cm')), axis.text.y=element_text(size=15, margin=unit(rep(0.30,4),'cm')), axis.text.y.right=element_text(size=15, margin=unit(rep(0.30,4),'cm')), panel.grid.minor=element_blank(), panel.grid.major=element_blank(), panel.background=element_rect(colour="black",size=4), plot.margin=unit(c(0.5,0.6,0.5,0.25),'cm'), legend.key=element_blank(), legend.position=c(0.5,0.2), legend.direction="vertical", legend.title.align=0, legend.background=element_rect(fill=NA), legend.box.background=element_rect(fill='white', size=0.5), legend.box='vertical', legend.key.size=unit(0.8, 'cm'),legend.title=element_text(size=16), legend.text=element_text(size=14), legend.spacing.y=unit(0.02, 'cm'), legend.spacing.x=unit(0.01, 'cm') )
bxp1
  

bxp2=ggplot(data=long_bxpdat_bioenergy, aes(x=variables, y=mean_values, group=interaction(treatment,variables), fill = NULL, linetype= treatment )) +  geom_boxplot(width=0.3) + 
  labs(x=NULL, y=NULL)  +   
  scale_x_discrete(expand=c(0.005,0.005),labels = NULL) + 
  scale_y_continuous(limits=c(0,80),breaks = seq(0,80, by = 20),labels = NULL,expand=c(0.005,0.005), sec.axis=sec_axis(~.*1,labels=NULL,breaks = seq(0,80, by = 20))) +
  theme_linedraw() + 
  #scale_fill_manual(values=lcols, labels = c('Jatropha', 'Maize'), name = 'Type of crop') +
  guides(colour='none', fill='none', linetype='none', alpha='none' ) +
  scale_linetype_manual(values=c("solid", "dashed"), name = "Treatment", labels = c('Interaction', 'No interaction'))  +
  theme(text=element_text(size=16), plot.title = element_text(hjust=0.5,vjust=3,color="black", size=18, face="bold.italic"), title=element_text(face='bold'), axis.ticks=element_line(size=0.75), axis.ticks.length=unit(-0.3,'cm'), axis.title.y=element_text(vjust=-1), axis.title.y.right = element_text(vjust=-1,color = 'black'), axis.text.x = element_text(vjust = -1, size=15, margin=unit(rep(0.30,4),'cm')), axis.text.y=element_text(size=15, margin=unit(rep(0.30,4),'cm')), axis.text.y.right=element_text(size=15, margin=unit(rep(0.30,4),'cm')), panel.grid.minor=element_blank(), panel.grid.major=element_blank(), panel.background=element_rect(colour="black",size=4), plot.margin=unit(c(0.25,0.6,1.1,0.25),'cm'), legend.key=element_blank(), legend.position=c(0.5,0.2), legend.direction="vertical", legend.title.align=0, legend.background=element_rect(fill=NA), legend.box.background=element_rect(fill='white', size=0.5), legend.box='vertical', legend.key.size=unit(0.8, 'cm'),legend.title=element_text(size=16), legend.text=element_text(size=14), legend.spacing.y=unit(0.02, 'cm'), legend.spacing.x=unit(0.01, 'cm') )
bxp2


## ------------------------------------------------------------------------------------------------------------
## combine plot
quartz(file= '/Users/kwabx/labspaces/bioenergy_landuse_conflict_model/data/work/result.pdf', type='pdf', dpi=2500, width=10, height=9, bg="white")
figure=ggarrange(ggarrange(plt1, bxp1, nrow = 1, ncol = 2, align = "h",widths = c(0.75,0.25),labels = c("A","B"), font.label = list(size = 20, color = "black"), vjust = c(2.5,2.5), hjust = c(-5.4,-1)),
                 ggarrange(plt2, bxp2, nrow = 1, ncol = 2, align = "h",widths = c(0.75,0.25),labels = c("C","D"), font.label = list(size = 20, color = "black"), vjust = c(2.5,2.5), hjust = c(-5.4,-1)),
                 nrow = 2, ncol = 1, align = "v", widths = c(1,1))
figure
graphics.off()

# quartz(file= '/Users/kwabx/labspaces/bioenergy_landuse_conflict_model/data/work/result.pdf', type='pdf', dpi=2500, width=10, height=9, bg="white")
# figure=ggarrange(plt1,bxp1,
#                  plt2,bxp2,
#                  nrow = 2, ncol = 2, align = "h", widths = c(0.75,0.25), heights = c(1,1),
#                  labels = '', font.label = list(size = 20, color = "black"),
#                  vjust = c(3,3), hjust = c(-6,-6))
# figure
# graphics.off()


## ------------------------------------------------------------------------------------------------------------
source("pairwise_with_t_df.R") # to be able to extract t-values and dfs in pairwise comparison
## t-test for bioenergy (intercation vs no-interaction)
bioenergy_results=pairwise.t.test.with.t.and.df(long_bxpdat_bioenergy$mean_values,long_bxpdat_bioenergy$treatment,paired= FALSE, p.adjust.method = "none")
bioenergy_results$p.value ; bioenergy_results$t.value ; bioenergy_results$dfs

## t-test for food (intercation vs no-interaction)
food_results=pairwise.t.test.with.t.and.df(long_bxpdat_food$mean_values,long_bxpdat_food$treatment,paired= FALSE, p.adjust.method = "none")
food_results$p.value ; food_results$t.value ; food_results$dfs

