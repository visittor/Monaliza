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

#define MainMonalisa_C_SRC

/****************************************************************************/
/**                                                                        **/
/**                             MODULES USED                               **/
/**                                                                        **/
/****************************************************************************/

#include "MainMonalisa.h"


/****************************************************************************/
/**                                                                        **/
/**                        DEFINITIONS AND MACROS                          **/
/**                                                                        **/
/****************************************************************************/

#define CCW 0
#define CW 1
#define BREAK 2

#define MOTORIN1 PIN_A2
#define MOTORIN2 PIN_A4
#define ENABLEA1 PIN_B2

#define RadiusOfFaulhaber 7

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


static void HardwareInit();
void MotorMoving(int speed , int direction);
float computeInstantlyDistant(float distance);


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

int StateDirection = 1;
int countDistance = 0;

int stateCHA = 0;
int stateCHB = 0;

static volatile int16u timeOld = 0;
static volatile int16u timeNew = 0;
static volatile int16u directionRead = 0;
static volatile int16u interval = 65535;
static int16u t = 0;
static int c = 0;

PIDParameter MotorX ,MotorY;
float referenceDesire = 0;
float currentDistance = 0;
float error = 0;

int stateBackward = 0;

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
	disable_interrupts(INTR_GLOBAL);
	clear_interrupt(INT_EXT0);
	enable_interrupts(INT_EXT0);
	clear_interrupt(INT_EXT1);
	enable_interrupts(INT_EXT1);
	HardwareInit();
	enable_interrupts(INTR_GLOBAL);
	
	InitialPID(&MotorX);
	InitialPID(&MotorY);

	// MotorX.Kp = 200;
	// MotorX.Ki = 0;
	// MotorX.Kd = 2200 ;
	MotorX.Kp = 12;
	MotorX.Ki = 0.3;
	MotorX.Kd = 60 ;	

	referenceDesire = 200; // mm
	// printf("%f\n",referenceDesire);
	

	while(1)
	{

	}

}



static void HardwareInit()
{
	setup_adc_ports(NO_ANALOGS);
									 //  	1 2 3 4 	5 6 7 8		9 10 11 12   13 14 15 16 
	set_tris_a(get_tris_a() & 0xffeb); //   1 1 1 1     1 1 1 1     1  1  1  0    0	 0  0  0  
	set_tris_b(get_tris_b() & 0xfff3); //	1 1 1 1     1 1 1 1     1  1  1  1    0	 0  1  1

	output_high(LED0);
	output_high(LED1);
	output_high(LED2);
	output_high(LED3);

	set_compare_time(1,0);
	setup_compare(1,COMPARE_PWM | COMPARE_TIMER3);

	set_timer3(0);
	setup_timer3(TMR_INTERNAL | TMR_DIV_BY_1 , 999);
	/* FreqPWM = 16 MHz  / 10000 = 1.6 KHz | Now 16 KHz*/ 

	setup_capture(1, CAPTURE_EE | INTERRUPT_EVERY_CAPTURE | CAPTURE_TIMER2);
	clear_interrupt(INT_IC1);
	enable_interrupts(INT_IC1);

	setup_capture(2, CAPTURE_EE | INTERRUPT_EVERY_CAPTURE | CAPTURE_TIMER2);
	clear_interrupt(INT_IC2);
	enable_interrupts(INT_IC2);
	/* INPUT CAPTURE PULSE OF ENCODER */
	/* Try to read encoder and on/off led represent CHA CHB */

	set_timer2(0);
	setup_timer2(TMR_INTERNAL | TMR_DIV_BY_1 , 65535);
	

	clear_interrupt(INT_TIMER5);
	set_timer5(0);
	setup_timer5(TMR_INTERNAL | TMR_DIV_BY_256,6249);
	// disable_interrupts(INT_TIMER5);
	// enable_interrupts(INT_TIMER5);

	// MotorMoving(500,CCW);
}

void MotorMoving(int speed , int direction)
{
	if(speed > 750)
	{
		speed = 750;
	}

	if (direction == CCW)
	{
		set_pwm_duty(1,speed);
		output_high(MOTORIN1);
		output_low(MOTORIN2);
	}
	else if (direction == CW)
	{
		set_pwm_duty(1,speed);
		output_high(MOTORIN2);
		output_low(MOTORIN1);
	}
	else if (direction == BREAK)
	{
		set_pwm_duty(1,0);
		output_low(MOTORIN1);
		output_low(MOTORIN2);
	}

}

void computeInstantlyDistant()
{
	currentDistance = (((countDistance*(7.5/64))*3.14)/180)*RadiusOfFaulhaber;
}


#INT_TIMER5
void INT_TMR5()
{
	computeInstantlyDistant();
	error = referenceDesire - currentDistance;
	
	if( (int16)error > 1 || (int16)error < -1)
	{
		PIDVelocityForm(error,&MotorX);
		
		if(stateBackward == 1)
		{
			MotorMoving(750,CW);
		}
		else if(stateBackward == 0)
		{
			printf("%d,%d,%d\n",(int16)error, (int16)currentDistance,  (int16)MotorX.u);
			if(MotorX.u >= 0)
			{

				MotorMoving((int16)MotorX.u,CCW);
			}
			else if(MotorX.u < 0)
			{
				MotorMoving(-1*(int16)MotorX.u,CW);
			}
			// MotorMoving(750,CCW);
		}
	}
	else
	{
		MotorMoving(0,BREAK);
		printf("b\n");
	}
}


#INT_IC1
void testIC1()
{	
	int16u ip = (input_b () & 0x0030);

	timeNew = get_capture (1);
	interval = timeNew - timeOld;
	stateCHA = ~(((ip & 0x10)>>4) ^ ((ip & 0x20)>>5)) & 0x01;
	if ( (ip & 0x10)>>4 == (ip & 0x20)>>5 ) {
		directionRead = 1;
		countDistance += 1;
	}
	else{
		directionRead = 2;
		countDistance -= 1;
	}
	timeOld = timeNew;

}

#INT_IC2
void testIC2()
{
	int16u ip = (input_b () & 0x0030);
	timeNew = get_capture(2);

	interval = timeNew - timeOld;
	stateCHB = ((ip & 0x10)>>4) ^ ((ip & 0x20)>>5);
	if ( (ip & 0x10)>>4 != (ip & 0x20)>>5 ){
		directionRead = 1;
		countDistance += 1;
	}
	else{
		directionRead = 2;
		countDistance -= 1;
	}

	timeOld = timeNew;

}

#INT_EXT0
void INT_EXTT0()
{
	enable_interrupts(INT_TIMER5);	
	stateBackward = 0;
	// if(StateDirection == 1)
	// {
	// 	StateDirection = 2;
	// }
	// else if(StateDirection == 2)
	// {
	// 	StateDirection = 1;
	// }
}

#INT_EXT1
void INT_EXTT1()
{
	enable_interrupts(INT_TIMER5);
	stateBackward = 1;
}

/****************************************************************************/

/****************************************************************************/
/**                                                                        **/
/**                                 EOF                                    **/
/**                                                                        **/
/****************************************************************************/

	StatePID = 0;
	if(arrayPtr[1] == '1')
	{
		printf("PID\n");
		arrayPtr[2] = arrayPtr[2] - 48;
		arrayPtr[3] = arrayPtr[3] - 48;
		arrayPtr[4] = arrayPtr[4] - 48;
		arrayPtr[5] = arrayPtr[5] - 48;
		referenceDesireX = convert_8to16bit(arrayPtr[2],arrayPtr[3]); // mm
		referenceDesireY = convert_8to16bit(arrayPtr[4],arrayPtr[5]);
		StatePID = 1;
	}
	else if(arrayPtr[1] == '2')
	{
		printf("MotorX\n");
		StateBreakAxis = 2;
		StateBreak = 0;
		StateMotor = 0;
		if(arrayPtr[2] == '0')
		{
			printf("CCW\n");
			StateDirection = 0;
		}
		else if(arrayPtr[2] == '1')
		{
			printf("CW\n");
			StateDirection = 1;
		}
	}
	else if(arrayPtr[1] == '3')
	{
		printf("MotorY\n");
		StateBreakAxis = 2;
		StateBreak = 0;
		StateMotor = 1;
		if(arrayPtr[2] == '0')
		{
			printf("CCW\n");
			StateDirection = 0;
		}
		else if(arrayPtr[2] == '1')
		{
			printf("CW\n");
			StateDirection = 1;
		}
	}
	else if(arrayPtr[1] == '4')
	{
		printf("Break\n");
		StateBreak = 1;
		StateMotor = 2;
		StateDirection = 2;
		if(arrayPtr[2] == '0')
		{
			printf("X-Axis\n");
			StateBreakAxis = 0;
		}
		else if(arrayPtr[2] == '1')
		{
			printf("Y-Axis\n");
			StateBreakAxis = 1;
		}
	}
	else if(arrayPtr[1] == '5')
	{
		printf("CheckStatus\n");
	}
	else if(arrayPtr[1] == '6')
	{
		printf("SetZero\n");
		if(arrayPtr[2] == '0')
		{
			printf("X-Axis\n");
		}
		else if(arrayPtr[2] == '1')
		{
			printf("Y-Axis\n");
		}

	}
	else if(arrayPtr[1] == '9')
	{
		if(arrayPtr[2] == '1')
		{
			printf("Monalisa Activate!\n");
			enable_interrupts(INT_TIMER5);
		}
		else if(arrayPtr[2] == '0')
		{
			printf("Monalisa Deactivate!\n");
			disable_interrupts(INT_TIMER5);
		}
	}