/*
*************************** C SOURCE FILE ************************************

project   :
filename  : CTEMPLATE.C
version   : 2
date      :

******************************************************************************

Copyright (c) 20xx
All rights reserved.

******************************************************************************

VERSION HISTORY:
----------------------------
Version      : 1
Date         :
Revised by   :
Description  :

Version      : 2
Date         :
Revised by   :
Description  : *
               *
               *

******************************************************************************
*/

#define TestModule_C_SRC

/****************************************************************************/
/**                                                                        **/
/**                             MODULES USED                               **/
/**                                                                        **/
/****************************************************************************/

#include "TestModule.H"

/****************************************************************************/
/**                                                                        **/
/**                        DEFINITIONS AND MACROS                          **/
/**                                                                        **/
/****************************************************************************/
#define USINGPIDXY 1
#define DRIVEONLY 0

/****************************************************************************/
/**                                                                        **/
/**                        TYPEDEFS AND STRUCTURES                         **/
/**                                                                        **/
/****************************************************************************/


/****************************************************************************/
/**                                                                        **/
/**                      PROTOTYPES OF LOCAL FUNCTIONS                     **/
/**                                                                        **/
/****************************************************************************/
void HardwareInit();

/****************************************************************************/
/**                                                                        **/
/**                           EXPORTED VARIABLES                           **/
/**                                                                        **/
/****************************************************************************/


/****************************************************************************/
/**                                                                        **/
/**                            GLOBAL VARIABLES                            **/
/**                                                                        **/
/****************************************************************************/
PIDParameter PIDXAxis, PIDYAxis;
MotorParameter MotorX, MotorY;

static volatile int8u StatePID = USINGPIDXY;


/****************************************************************************/
/**                                                                        **/
/**                           EXPORTED FUNCTIONS                           **/
/**                                                                        **/
/****************************************************************************/


/****************************************************************************/
/**                                                                        **/
/**                             LOCAL FUNCTIONS                            **/
/**                                                                        **/
/****************************************************************************/

void main()
{
	DisableIntr();

	InitialPID(&PIDXAxis,20,0,0);
	InitialPID(&PIDYAxis,10,0,0);
	InitialMotorControl(&MotorX);
	InitialMotorControl(&MotorY);

	HardwareInit();
	InitialInterruptController();

	MotorX.referenceDesire = 100;
	MotorY.referenceDesire = 100;

	EnableIntr();
	while(1)
	{

	}

}


void HardwareInit()
{
	setup_adc_ports(NO_ANALOGS);
									 //  	1 2 3 4 	5 6 7 8		9 10 11 12   13 14 15 16 
	set_tris_a(get_tris_a() & 0xffe0); //   1 1 1 1     1 1 1 1     1  1  1  0    0	 0  0  0  
	set_tris_b(0xfffa); 				//	1 1 1 1     1 1 1 1     1  1  1  1    1	 0  1  0

	output_high(LED0);
	output_high(LED1);
	output_high(LED2);
	output_high(LED3);
}



#INT_TIMER5
void INTERRUPTFUNCTIONOFTIMER5()
{

	if(StatePID == DRIVEONLY)
	{
		MovingMotor(XAXIS,500,CW);
		// printf("DRIVEONLY\n");

		// printf("%d\n",(int16u)MotorY.countDistance );
	}

	else if(StatePID == USINGPIDXY)
	{

		computeDistance(&MotorX);
		computeDistance(&MotorY);
		PIDXAxis.error = MotorX.referenceDesire - MotorX.currentDistance;
		PIDYAxis.error = MotorY.referenceDesire - MotorY.currentDistance;
		// printf("%d,%d,%d\n",(int16u)PIDXAxis.error,(int16u)MotorX.referenceDesire,(int16u)PIDXAxis.u);
		// printf("%d\n", (int16u)MotorX.countDistance);
		if(abs(PIDXAxis.error) > 1)
		{
			PIDVelocityForm(&PIDXAxis);
			if(PIDXAxis.u >= 0)
			{
				MovingMotor(XAXIS,(int16)PIDXAxis.u,CCW);
			}
			else if(PIDXAxis.u < 0)
			{
				MovingMotor(XAXIS,-1*(int16)PIDXAxis.u,CW);
			}
		}
	

		if(abs(PIDYAxis.error) > 1)
		{
			PIDVelocityForm(&PIDYAxis);
			if(PIDYAxis.u >= 0)
			{
				MovingMotor(YAXIS,(int16)PIDYAxis.u,CCW);
			}
			else if(PIDYAxis.u < 0)
			{
				MovingMotor(YAXIS,-1*(int16)PIDYAxis.u,CW);
			}
		}
	}
	
}

#INT_IC1
void READENCODERCHANNELAXAXIS()
{
	// printf("Capture1.1\n");
	qudratureEncoderChannelAXAxis(&MotorX);
}

#INT_IC2
void READENCODERCHANNELBXAXIS()
{
	// printf("Capture1.2\n");
	qudratureEncoderChannelBXAxis(&MotorX);
}

#INT_IC3
void READENCODERCHANNELAYAXIS()
{
	qudratureEncoderChannelAYAxis(&MotorY);
}

#INT_IC4
void READENCODERCHANNELBYAXIS()
{
	qudratureEncoderChannelBYAxis(&MotorY);
}


/****************************************************************************/

/****************************************************************************/
/**                                                                        **/
/**                                 EOF                                    **/
/**                                                                        **/
/****************************************************************************/