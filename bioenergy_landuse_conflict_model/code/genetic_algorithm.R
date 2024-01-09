
#----------------------------------------------------------------------------
# Genetic algorithm ode 
# By: Kwabena Afriyie, Owusu
# Created: 21.12.2023
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

#----------------------------------------------------------------------------
## real data of maize production in Brong-Ahafo from 2018-2022 (set at 22% of national production)
year = c(2018:2022)
production = c(507320.0, 638000.0, 667040.0, 704660.0, 748220.0)
realdat = data.frame(year,production)
realdat$year <- as.numeric(as.vector(realdat$year)) 
realdat$production <- as.numeric(as.vector(realdat$production)) 
realdat$production <- realdat$production / 1000

# plot realdat
plt=ggplot(data=realdat, aes(x=year, y=production)) +  geom_line(size=0.6) +
  geom_point(aes(y=production), shape=16,size=4) + 
  labs(x=TeX(r"(\textbf{Year})"), y=TeX(r"(\textbf{Production ${(x \; 10^3 \; tons)}}$)")) +
  ggtitle(TeX(r"(\textbf{Maize production in Brong-Ahafo region, Ghana (2018 - 2022)})")) +
  scale_x_continuous(limits=c(2018,2022), breaks = seq(2018, 2022, by = 1), expand=c(0.01,0.01), sec.axis=sec_axis(~.*1,labels=NULL,breaks = seq(2018, 2022, by = 1))) +
  scale_y_continuous(limits=c(500,800), breaks = seq(500, 800, by = 50),expand=c(0.005,0.005), sec.axis=sec_axis(~.*1,labels=NULL,breaks = seq(500, 800, by = 50))) +
  theme_linedraw() +
  theme(text=element_text(size=18), plot.title = element_text(hjust=0.5,vjust=3,color="black", size=18, face="bold.italic"), title=element_text(face='bold'), axis.ticks=element_line(size=0.75), axis.ticks.length=unit(-0.3,'cm'), axis.title.y=element_text(vjust=-1), axis.title.y.right = element_text(vjust=-1,color = 'black'), axis.text.x = element_text(vjust = -1, size=15, margin=unit(rep(0.30,4),'cm')), axis.text.y=element_text(size=15, margin=unit(rep(0.30,4),'cm')), axis.text.y.right=element_text(size=15, margin=unit(rep(0.30,4),'cm')), panel.grid.minor=element_blank(), panel.grid.major=element_blank(), panel.background=element_rect(colour="black",size=4), plot.margin=unit(c(0.5,0.6,1.1,0.25),'cm'), legend.key=element_blank(), legend.position=c(0.5,0.9), legend.direction="horizontal", legend.title.align=0, legend.background=element_rect(fill=NA), legend.box.background=element_rect(fill='white', size=0.5), legend.box='vertical', legend.key.size=unit(0.8, 'cm'),legend.title=element_text(size=16), legend.text=element_text(size=14), legend.spacing.y=unit(0.02, 'cm'), legend.spacing.x=unit(0.01, 'cm') )
plt
quartz(file= '/Users/kwabx/labspaces/bioenergy_landuse_conflict_model/data/work/realdat_Brong_Ahafo.pdf', type='pdf', dpi=2500, width=10, height=6, bg="white")
figure=ggarrange(plt)
figure
graphics.off()



#----------------------------------------------------------------------------
## simualtion genetic calibration data ##
n=40 # number of generations
for(gen in 0:n){

  gen_path<-list.files(sprintf("/Users/kwabx/labspaces/bioenergy_landuse_conflict_model/data/work/genetic_calibration_data/generation_%s",gen) , pattern=".csv", full.names=TRUE, recursive=TRUE) # list all files in the directory formated according to their name conventions
  gen_path

  timdat<-data.frame( time=c(), price_bioenergy=c(), price_food=c(), harvest_bioenergy=c(),
                      harvest_food=c(), land_fertility=c(), priority_food=c(), priority_bioenergy=c(),
                      priority_fallow=c(),land_food=c(), land_bioenergy=c(),capital=c(), food_direction=c(),
                      bioenergy_direction=c(), no_interaction=c(), yes_interaction=c(), treatment=c(), NoSim=c())

  for(fi in gen_path){
    infile<-read.table(fi, sep=',' ,header=T)
    infile<-data.frame(infile, time=rep(1:6,dim(infile)[1]/6))  #infile<-data.frame(infile, time=rep(1:6,dim(infile)[1]/6))  
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
                     NoSim = infile$NoSim
    )
    timdat<-rbind(timdat, ttpp)
  }

  solution <- rep(1:20, each = 18) # combine solutions for a generation in one dataframe
  solution <- data.frame(solution)
  timdat <- cbind(solution,timdat)

  timdat_mean <- timdat %>% filter(time > 0) %>%  group_by(solution,time) %>% summarise(N=n(),                                # because time zero is the initialization
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
                                                                                        capital = mean(capital, na.rm = T)) #%>% filter(time < -1)

  long_timdat_mean <- timdat_mean %>% gather(variables, mean_values, harvest_food) # change from wide to long format
  long_timdat_mean$time <- as.numeric(as.vector(long_timdat_mean$time)) # x-axis treated as continuous variable
  long_timdat_mean$solution<- as.factor(long_timdat_mean$solution) # treatment treated as factor variable
  long_timdat_mean$mean_values <- long_timdat_mean$mean_values /1000

  #### plotting both real and simulation data ####
  assign(noquote(sprintf("plt%s",gen)), # assign used instead of -> and noquotes used to remove quotation, sprintf used to merge name
         ggplot(data=long_timdat_mean, aes(x=rep(realdat$year,20), y=mean_values, group=interaction(solution,variables), color=variables)) +  geom_line(aes()) +  # 20 solutions
           labs(x=TeX(r"(\textbf{Year})"), y=TeX(r"(\textbf{Production ${(x \; 10^3 \; tons)}}$)")) +
           ggtitle(noquote(sprintf("Generation %s",gen)))  +
           scale_x_continuous(limits=c(2018,2022), breaks = seq(2018, 2022, by = 1), expand=c(0.011,0.011), sec.axis=sec_axis(~.*1,labels=NULL,breaks = seq(2018, 2022, by = 1))) +
           #scale_x_continuous(limits=c(1,12), breaks = seq(1, 12, by = 1), expand=c(0.005,0.005), sec.axis=sec_axis(~.*1,labels=NULL,breaks = seq(1, 12, by = 1))) +
           scale_y_continuous(limits=c(400,800),breaks = seq(400, 800, by = 100),expand=c(0.005,0.005), sec.axis=sec_axis(~.*1,labels=NULL,breaks = seq(400, 800, by = 100))) +
           geom_point(aes(x=rep(realdat$year,20), y=rep(realdat$production,20),color='red'),size=2, shape=16) +
           theme_linedraw() +
           # scale_colour_manual(values=lcols, name = "Type of crop", labels = c('Jatropha', 'Maize')) +
           # scale_linetype_manual(values=c("solid", "dashed"), name = "Treatment", labels = c('Interaction', 'No interaction'))  +
           # geom_hline(yintercept=35000, linetype="solid", color = "black", size=0.5) +
           # scale_size_manual(values = c(1,1),labels = NULL, name=NULL,guide = FALSE) +
           scale_colour_manual(values = c("dark grey", "black"), name = "", labels = c('Simulation data', 'Real data'),
                               guide = guide_legend(override.aes = list(
                                 linetype = c("solid", "blank"),
                                 shape = c(NA, 16)))) +
           # #scale_color_discrete(name = "Harvest", labels = c('Bioenergy crop', 'Food crop')) +
           # #scale_linetype_manual(values=c('solid', 'dotted'), labels = c('Bioenergy crop', 'Food crop')) +
           # #guides(colour='none', fill=guide_legend(direction='horizontal', title.position='top', label.position='right'), linetype='none', alpha=guide_legend(direction='horizontal', title.position='top', label.position='right', override.aes=list(fill=c(alpha('grey', 0.0), alpha('grey', 0.8))) ) ) +
           #theme(text=element_text(size=16), title=element_text(face='bold'), axis.ticks=element_line(size=0.75), axis.ticks.length=unit(-0.3,'cm'), axis.title.y=element_text(vjust=-1),axis.text.x = element_text(vjust = -1, size=13, margin=unit(rep(0.30,4),'cm')) ,axis.text.y=element_text(size=13, margin=unit(rep(0.30,4),'cm')),  panel.grid.minor=element_blank(), panel.grid.major=element_blank(), panel.background=element_rect(colour="black",size=4), plot.margin=unit(c(0.5,0.6,1.1,0.25),'cm'), legend.key=element_blank(), legend.position=c(0.85,0.8), legend.direction='vertical', legend.title.align=0, legend.background=element_rect(fill=NA), legend.box.background=element_rect(fill='white', size=0.5), legend.box='vertical', legend.key.size=unit(0.45, 'cm'),legend.title=element_text(size=11), legend.text=element_text(size=11), legend.spacing.y=unit(0.01, 'cm'), legend.spacing.x=unit(0.01, 'cm') )
           theme(text=element_text(size=18), plot.title = element_text(hjust=0.5,vjust=3,color="black", size=18, face="bold.italic"), title=element_text(face='bold'), axis.ticks=element_line(size=0.75), axis.ticks.length=unit(-0.3,'cm'), axis.title.y=element_text(vjust=-1), axis.title.y.right = element_text(vjust=-1,color = 'black'), axis.text.x = element_text(vjust = -1, size=15, margin=unit(rep(0.30,4),'cm')), axis.text.y=element_text(size=15, margin=unit(rep(0.30,4),'cm')), axis.text.y.right=element_text(size=15, margin=unit(rep(0.30,4),'cm')), panel.grid.minor=element_blank(), panel.grid.major=element_blank(), panel.background=element_rect(colour="black",size=4), plot.margin=unit(c(0.5,0.6,1.1,0.25),'cm'), legend.key=element_blank(), legend.position=c(0.5,0.2), legend.direction='horizontal', legend.title.align=0, legend.background=element_rect(fill=NA), legend.box.background=element_rect(fill='white', size=0.5), legend.box='vertical', legend.key.size=unit(0.8, 'cm'),legend.title=element_text(size=16), legend.text=element_text(size=14), legend.spacing.y=unit(0.01, 'cm'), legend.spacing.x=unit(0.01, 'cm') )
         #noquote(sprintf("plt%s",gen))
  )
}


### Combine plots
quartz(file= '/Users/kwabx/labspaces/bioenergy_landuse_conflict_model/data/work/genetic_calibration.pdf', type='pdf', dpi=2500, width=20, height=12, bg="white")
figure=ggarrange(plt0,plt1,plt2,plt3,plt4,plt5,plt6,plt7,plt8,plt9,plt10,
                 plt11,plt12,plt13,plt14,plt15,plt16,plt17,plt18,plt19,plt20,
                 plt21,plt22,plt23,plt24,plt25,plt26,plt27,plt29, plt30,plt31,
                 plt32,plt33,plt34,plt35,plt36,plt37,plt38,plt39,plt40,
#   plt41,plt42,plt43,plt44,plt45,
#   plt46,plt47,plt48,plt49,plt50,plt51,plt52,plt53,plt54,
#   plt55,plt56,plt57,plt58,plt59,plt60,plt61,plt62,plt63,
#   plt64,plt65,plt66,plt67,plt68,plt69,plt70,plt71,plt72,
#   plt73,plt74,plt75,plt76,plt77,plt78,plt79,plt80,plt81,
#   plt82,plt83,plt84,plt85,plt86,plt87,plt88,plt89,plt90,
#   plt91,plt92,plt93,plt94,plt95,plt96,plt97,plt98,plt99,plt100,
#   plt101,plt102,plt103,plt104,plt105,plt106,plt107,plt108,plt109,plt110,
#   plt111,plt112,plt113,plt114,plt115,plt116,plt117,plt118,plt119,plt120,
#   plt121,plt122,plt123,plt124,plt125,plt126,plt127,plt128,
#   plt129,plt130,plt131,plt132,plt133,plt134,plt135,plt136,
#   plt137,plt138,plt139,plt140,plt141,plt142,plt143,plt144,plt145,plt146,
  nrow = 3, ncol = 3, align = "h", widths = c(1,1,1),heights = c(1,1,1),
  labels = '', font.label = list(size = 20, color = "black"),
  vjust = c(2.5,2.5,2.5), hjust = c(-6,-6,-6) ,common.legend = TRUE, legend = "top")
figure
graphics.off()



#------------------------------------------------------------------------------------------------------------------------------
## select parameters with highest fitness

lstfile<-c("/Users/kwabx/labspaces/bioenergy_landuse_conflict_model/data/work/genetic_calibration.csv")
param_dat<-data.frame(GENERATION=c(),	COST_BIOENERGY=c(),	YIELD_BIOENERGY=c(),	INIT_PRICE_BIOENERGY=c(),	AMOUNT_DEMAND_BIOENERGY=c(),	FITNESS=c()) 
for(fi in lstfile){
  infile1<-read.table(fi, sep=",", header = T)
  infile1<-data.frame(infile1)
  ttpp<-data.frame(GENERATION = infile1$GENERATION,
                   COST_BIOENERGY= infile1$COST_BIOENERGY,
                   YIELD_BIOENERGY = infile1$YIELD_BIOENERGY,
                   INIT_PRICE_BIOENERGY = infile1$INIT_PRICE_BIOENERGY,
                   AMOUNT_DEMAND_BIOENERGY = infile1$AMOUNT_DEMAND_BIOENERGY,
                   FITNESS = infile1$FITNESS)
  param_dat<-rbind(param_dat, ttpp)
}
param_dat = param_dat %>%mutate_all(funs(ifelse(is.na(.), 0, .)))

param_dat$GENERATION <- as.factor(param_dat$GENERATION) 
param_dat_fitness <- param_dat %>%filter(FITNESS == min(FITNESS))  # # select parameters generating highest fitness (i.e. lowest RMSE)) for each generation    
# param_dat_fitness <- param_dat %>%  group_by(GENERATION) %>%  filter(FITNESS == min(FITNESS))  # # select parameters generating highest fitness (i.e. lowest RMSE)) for each generation    
param_dat_fitness








































                                                                 
                                                                 
                                                                 
                                                                