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

//UART Rx frame
#define RX1Q_LN 8
#define RX_CMND_FRM_LN 16
#define START_CHR 0Xff
#define ID 1


//UART Queue
#define TX1Q_LN 128

#define CCW 0
#define CW 1
#define BREAK 2

#define MOTORINX1 PIN_A2
#define MOTORINX2 PIN_A4
#define ENABLEAX1 PIN_B2

#define MOTORINY1 PIN_A0
#define MOTORINY2 PIN_A1
#define ENABLEAY1 PIN_B0



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
static void GlobalVarInit();
static void DynamicMemInit();
static void UARTQueueInit();
static int8u SendTx1(int8u *strPtr);

void MotorMoving(int speed , int direction);
void computeInstantlyDistantX(float distance);
void computeInstantlyDistantY(float distance);

void CheckProtocal(int8u *arrayPtr);
int16u convert_8to16bit(int8u baseHightbyte, int8u baseLowbyte);
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
static volatile Q8UX_STRUCT Tx1QCB;
static volatile int8u Tx1QArray[TX1Q_LN];
static volatile int8u *Tx1BuffPtr;
static volatile int16u Tx1BuffIdx;
static volatile TX1_STATUS Tx1Flag;
static volatile int16u Tx1FrameIn, Tx1FrameOut, Rx1FrameCount,RxCount,Tx1QFullCount, Rx1QFullCount;
static volatile int8u *RxBuffPtr;
static volatile QPTRX_STRUCT Rx1QCB;
static volatile PTR_STRUCT Rx1BuffPtrArray[RX1Q_LN];
static volatile PTR_STRUCT DestPtrStruct;
static volatile int8u Send_Buffer[20];

static volatile int16u MemFail,MemCount;

// int StateDirection = 1;
int countDistance = 0;

int stateCHAX = 0;
int stateCHBX = 0;

int stateCHAY = 0;
int stateCHBY = 0;

static volatile int16u timeOldX = 0;
static volatile int16u timeNewX = 0;
static volatile int16u directionReadX = 0;
static volatile int16u intervalX = 65535;
static int16u tX = 0;
static int cX = 0;

static volatile int16u timeOldY = 0;
static volatile int16u timeNewY = 0;
static volatile int16u directionReadY = 0;
static volatile int16u intervalY = 65535;
static int16u tY = 0;
static int cY = 0;

PIDParameter MotorX ,MotorY;
float referenceDesireX = 0;
float currentDistanceX = 0;
float referenceDesireY = 0;
float currentDistanceY = 0;

int16u countDistanceX = 0;
int16u countDistanceY = 0;

float errorX = 0;
float errorY = 0;
int8u distantofX = 0;
int8u distantofY = 0;

int stateBackward = 0;
int StatePID = 0;


static volatile int16u speedX = 0;
static volatile int16u speedY = 0;


//*********************************
//******** State Variable ********
// temporary protocal 
// moving desire distant pid <1 x x y y>
// moving x <2 0 or 1> 0 = CCW , 1 = CW
// moving y <3 0 or 1> 0 = CCW , 1 = CW
// break <3 0 or 1> 0 = X , 1 = Y
// Check status <4 1>
// set zero <5 0 or 1> 0 = X , 1 = Y  
// static volatile int8u StatePID = 0;
static volatile int8u StateMotorX = 0; // 0 = X , 1 = Y
static volatile int8u StateMotorY = 0;
static volatile int8u StateDirectionX = 0;
static volatile int8u StateDirectionY = 0; // 0 = CCW , 1 = CW
static volatile int8u StateBreak = 0;
static volatile int8u StateBreakX = 0; // 0 = X , 1 = Y 
static volatile int8u StateBreakY = 0;
static volatile int8u StateResetX = 0;
static volatile int8u StateResetY = 0;
//*********************************

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
void main ()
{	
	InitialPID(&MotorX);
	InitialPID(&MotorY);

	// MotorX.Kp = 200;
	// MotorX.Ki = 0;
	// MotorX.Kd = 2200 ;
	// MotorX.Kp = 12;
	// MotorX.Ki = 0.3;
	// MotorX.Kd = 60 ;

	MotorX.Kp = 10;
	MotorX.Ki = 0;
	MotorX.Kd = 0 ;
	
	MotorY.Kp = 10;
	MotorY.Ki = 0;
	MotorY.Kd = 0;	

	int8u errCode, SendTx1Count;
	DisableIntr();
	clear_interrupt(INT_EXT1);
	enable_interrupts(INT_EXT1);
    clear_interrupt(INT_EXT2);
    enable_interrupts(INT_EXT2);
	ext_int_edge(1,H_TO_L);
	ext_int_edge(2,H_TO_L);
	HardwareInit();
	GlobalVarInit();
	DynamicMemInit();
	UARTQueueInit();
	EnableIntr();
	for (;;)
	{
		/* code */
		DisableIntr();
		QPtrXGet(&Rx1QCB,&DestPtrStruct,&errCode);
		if(errCode == Q_OK)
		{
			// SendTx1Count = SendTx1((int8u *)DestPtrStruct.blockPtr);
			CheckProtocal((int8u *)DestPtrStruct.blockPtr);
			free ((void *)DestPtrStruct.blockPtr);
			MemCount--;
			EnableIntr();
			if (SendTx1Count == 0)
			{
				/* code */
				output_low(LED3);
			}
		}
		else
		{
			EnableIntr();
		}
	}
}

/****************************************************************************/
static void HardwareInit()
{
	setup_adc_ports(NO_ANALOGS);
									 //  	1 2 3 4 	5 6 7 8		9 10 11 12   13 14 15 16 
	set_tris_a(get_tris_a() & 0xffe0); //   1 1 1 1     1 1 1 1     1  1  1  0    0	 0  0  0  
	set_tris_b(0xfffa); 				//	1 1 1 1     1 1 1 1     1  1  1  1    1	 0  1  0

	output_high(LED0);
	output_high(LED1);
	output_high(LED2);
	output_high(LED3);

	set_compare_time(1,0);
	setup_compare(1,COMPARE_PWM | COMPARE_TIMER3);

	set_compare_time(2,0);
	setup_compare(2,COMPARE_PWM | COMPARE_TIMER3);

	set_timer3(0);
	setup_timer3(TMR_INTERNAL | TMR_DIV_BY_1 , 999);
	/* FreqPWM = 16 MHz  / 10000 = 1.6 KHz | Now 16 KHz*/ 

	setup_capture(1, CAPTURE_EE | INTERRUPT_EVERY_CAPTURE | CAPTURE_TIMER2);
	clear_interrupt(INT_IC1);
	enable_interrupts(INT_IC1);

	setup_capture(2, CAPTURE_EE | INTERRUPT_EVERY_CAPTURE | CAPTURE_TIMER2);
	clear_interrupt(INT_IC2);
	enable_interrupts(INT_IC2);

	setup_capture(3, CAPTURE_EE | INTERRUPT_EVERY_CAPTURE | CAPTURE_TIMER2);
	clear_interrupt(INT_IC3);
	enable_interrupts(INT_IC3);

	setup_capture(4, CAPTURE_EE | INTERRUPT_EVERY_CAPTURE | CAPTURE_TIMER2);
	clear_interrupt(INT_IC4);
	enable_interrupts(INT_IC4);
	/* INPUT CAPTURE PULSE OF ENCODER */
	/* Try to read encoder and on/off led represent CHA CHB */

	set_timer2(0);
	setup_timer2(TMR_INTERNAL | TMR_DIV_BY_1 , 65535);
	

	clear_interrupt(INT_TIMER5);
	set_timer5(0);
	setup_timer5(TMR_INTERNAL | TMR_DIV_BY_256,6249);
	enable_interrupts(INT_TIMER5);
	// disable_interrupts(INT_TIMER5);
	// enable_interrupts(INT_TIMER5);

	// MotorMoving(500,CCW);
}
static void GlobalVarInit()
{
	Tx1Flag = TX1_READY;
	Tx1BuffIdx = 0;
	Tx1FrameIn = 0;
	Tx1FrameOut = 0;
	Tx1QFullCount = 0;
	Rx1FrameCount = 0;
	RxCount = 0;
	Rx1QFullCount = 0;
	MemFail = 0;
	MemCount = 0;
	return;
}

static void DynamicMemInit()
{
	RxBuffPtr = (int8u *)malloc ((sizeof (int8u)) * RX_CMND_FRM_LN);
	if (RxBuffPtr != (int8u *)NULL)
	{
		MemCount++;
		clear_interrupt(INT_RDA);
		enable_interrupts(INT_RDA);
	}
	else
	{
		MemFail++;
	}
	return;
}

static void UARTQueueInit()
{
	QPtrXInit (&Rx1QCB, Rx1BuffPtrArray, RX1Q_LN);
	Q8UXInit(&Tx1QCB,Tx1QArray,TX1Q_LN);
	return;
}
static int8u SendTx1 (int8u *strPtr)
{
	int8u strLn;
	int8u strIdx;
	int16u qSpace;
	int8u errCode;
	int8u count;
	count = 0;
	strLn = strPtr[3]+4;
	if (strLn != 0)
	{
		/* code */
		qSpace = TX1Q_LN - Q8UXCount(&Tx1QCB);
		if (qSpace >= (int16u)strLn)
		{
			/* code */
			for(strIdx = 0; strIdx < strLn; strIdx++)
			{
				Q8UXPut(&Tx1QCB,strPtr[strIdx],&errCode);
				count++;
			}
			if(Tx1Flag == TX1_READY)
			{
				Tx1Flag = TX1_BUSY;
				TX1IF = 1;
				enable_interrupts(INT_TBE);
			}
		}
	}
	return count;
}

void MotorMovingX(int speed , int direction)
{
	if(speed >= 750)
	{
		speed = 750;
	}

	if (direction == CCW)
	{
		set_pwm_duty(1,speed);
		output_high(MOTORINX1);
		output_low(MOTORINX2);
	}
	else if (direction == CW)
	{
		set_pwm_duty(1,speed);
		output_high(MOTORINX2);
		output_low(MOTORINX1);
	}
	else if (direction == BREAK)
	{
		set_pwm_duty(1,0);
		output_low(MOTORINX1);
		output_low(MOTORINX2);
	}

}

void MotorMovingY(int speed , int direction)
{
	if(speed >= 750)
	{
		speed = 750;
	}

	if (direction == CW)
	{
		set_pwm_duty(2,speed);
		output_high(MOTORINY1);
		output_low(MOTORINY2);
	}
	else if (direction == CCW)
	{
		set_pwm_duty(2,speed);
		output_high(MOTORINY2);
		output_low(MOTORINY1);
	}
	else if (direction == BREAK)
	{
		set_pwm_duty(2,0);
		output_low(MOTORINY1);
		output_low(MOTORINY2);
	}

}

void computeInstantlyDistantX()
{
	currentDistanceX = (((countDistanceX*(7.5/64))*3.14)/180)*RadiusOfFaulhaber;
}

void computeInstantlyDistantY()
{
	currentDistanceY = (((countDistanceY*(7.5/64))*3.14)/180)*RadiusOfFaulhaber;
}

void CheckProtocal(int8u *arrayPtr)
{
	StateResetX = 0;
	StateResetY = 0;
	StateBreakX = 0;
	StateBreakY = 0;
	StateMotorX = 0;
	StateMotorY = 0;
	StatePID = 0;
	if(arrayPtr[0] == 0xff)
	{
		if(arrayPtr[1] == 0xff)
		{
			if(arrayPtr[2] == 0x01)
			{
				if(arrayPtr[4] == 0)
				{
					// printf("Monalisa Activate\n");
					// printf("Reset!\n");
					// StateResetX = 1;
					// StateResetY = 1;
					StateMotorX = 1;
					StateBreakX = 0;
					StateDirectionX = 1;
					speedX = 300;
					StateMotorY = 1;
					StateBreakY = 0;
					StateDirectionY = 1;
					speedY = 500;
				}

				if(arrayPtr[4] == 9)
				{
					speedX = convert_8to16bit(arrayPtr[5],arrayPtr[6]);
					StateMotorX = 1;
					StateBreakX = 0;
					if(arrayPtr[7] == 0)
					{
						StateDirectionX = 0;
					}
					else if(arrayPtr[7] == 1)
					{
						StateDirectionX = 1;
					}
				}
				else if(arrayPtr[4] == 10)
				{
					speedY = convert_8to16bit(arrayPtr[5],arrayPtr[6]);
					StateMotorY = 1;
					StateBreakY = 0;
					if(arrayPtr[7] == 0)
					{
						StateDirectionY = 0;
					}
					else if(arrayPtr[7] == 1)
					{
						StateDirectionY = 1;
					}
				}

				if(arrayPtr[4] == 12)
				{
					// StateDirectionX = 2;
					// StateMotor = 2;
					if(arrayPtr[5] == 9)
					{
						StateBreakX = 1;
						StateMotorX = 0;
						speedX = 0;
						MotorMovingX(0,BREAK);
					}
					else if(arrayPtr[5] == 10)
					{
						StateBreakY = 1;
						StateMotorY = 0;
						speedY = 0;
						MotorMovingY(0,BREAK);
					}
				}
				if(arrayPtr[4] == 7)
				{
					referenceDesireX = convert_8to16bit(arrayPtr[5], arrayPtr[6]);
					referenceDesireY = convert_8to16bit(arrayPtr[7], arrayPtr[8]);
					StatePID = 1;
					MotorMovingX(0, BREAK);
					MotorMovingY(0, BREAK);
				}
				if(arrayPtr[4] == 8)
				{
					int16u high_byteX,low_byteX,high_byteY,low_byteY;
					high_byteX = ((int16u)currentDistanceX & 0xff00)>>8;
					low_byteX = ((int16u)currentDistanceX & 0x00ff);
					high_byteY = ((int16u)currentDistanceY & 0xff00)>>8;
					low_byteY = ((int16u)currentDistanceY & 0x00ff);
					Send_Buffer[0] = 255;
					Send_Buffer[1] = 255;
					Send_Buffer[2] = 1;
					Send_Buffer[3] = 7;
					Send_Buffer[4] = 8;
					Send_Buffer[5] = (int8u)high_byteX;
					Send_Buffer[6] = (int8u)low_byteX;
					Send_Buffer[7] = (int8u)high_byteY;
					Send_Buffer[8] = (int8u)low_byteY;
					Send_Buffer[9] = (input_b () & 0xff00)>>8;
					Send_Buffer[10] = 0x0f;
					SendTx1(Send_Buffer);
				}
			}
		}
	}
}

int16u convert_8to16bit(int8u baseHightbyte, int8u baseLowbyte)
{	
	return ((int16u)baseHightbyte<<8) | ((int16u)baseLowbyte);
}

#INT_TIMER5
void INT_TMR5()
{
	computeInstantlyDistantX();
	computeInstantlyDistantY();
	if(StateResetX == 1)
	{
		MotorMovingX(300,CW);
	}
	if(StateResetY == 1)
	{
		MotorMovingY(500,CW);
	}

	if(StateMotorX == 1)
	{
		if(StateDirectionX == 0)
		{
			MotorMovingX(speedX,CCW);
		}
		else if(StateDirectionX == 1)
		{
			MotorMovingX(speedX,CW);
		}
	}
	
	if(StateMotorY == 1)
	{
		if(StateDirectionY == 0)
		{
			MotorMovingY(speedY,CCW);
		}
		else if(StateDirectionY == 1)
		{
			MotorMovingY(speedY,CW);
		}
	}

	if(StateBreakX == 1)
	{
		MotorMovingX(0,BREAK);
	}
	if(StateBreakY == 1)
	{
		MotorMovingY(0,BREAK);
	}

	if(StatePID == 1)
	{

		errorX = referenceDesireX - currentDistanceX;
		errorY = referenceDesireY - currentDistanceY;

		if( abs(errorX) > 1)
		{
			PIDVelocityForm(errorX,&MotorX);
			if(MotorX.u >= 0)
			{
				MotorMovingX((int16)MotorX.u,CCW);
			}
			else if(MotorX.u < 0)
			{
				MotorMovingX(-1*(int16)MotorX.u,CW);
			}
		}
		else
		{
			MotorMovingX(0,BREAK);

		}

		if( abs(errorY) > 1)
		{
			PIDVelocityForm(errorY,&MotorY);
			if(MotorY.u >= 0)
			{
				MotorMovingY((int16)MotorY.u,CW);
			}
			else if(MotorY.u < 0)
			{
				MotorMovingY((int16)(-1*MotorY.u),CCW);
			}
		}
		else
		{
			MotorMovingY(0,BREAK);
		}
	}

	// printf("%d,%d,%d,%d\n", (int16)MotorX.u,(int16)errorX,(int16)referenceDesireX,(int16)countDistanceX);

	// printf("%d,%d,%d,%d\n", (int16)MotorY.u,(int16)errorY,(int16)referenceDesireY,(int16)countDistanceY);


}


#INT_IC1
void testIC1()
{	
	int16u ipX = (input_b () & 0x0030);

	timeNewX = get_capture (1);
	intervalX = timeNewX - timeOldX;
	stateCHAX = ~(((ipX & 0x10)>>4) ^ ((ipX & 0x20)>>5)) & 0x01;
	if ( (ipX & 0x10)>>4 == (ipX & 0x20)>>5 ) {
		directionReadX = 1;
		countDistanceX += 1;
	}
	else{
		directionReadX = 2;
		countDistanceX -= 1;
	}
	timeOldX = timeNewX;
	// computeInstantlyDistantX();

}

#INT_IC2
void testIC2()
{
	int16u ipX = (input_b () & 0x0030);
	timeNewX = get_capture(2);

	intervalX = timeNewX - timeOldX;
	stateCHBX = ((ipX & 0x10)>>4) ^ ((ipX & 0x20)>>5);
	if ( (ipX & 0x10)>>4 != (ipX & 0x20)>>5 ){
		directionReadX = 1;
		countDistanceX += 1;
	}
	else{
		directionReadX = 2;
		countDistanceX -= 1;
	}

	timeOldX = timeNewX;
	// computeInstantlyDistantX();

}

#INT_IC3
void testIC3()
{	
	int16u ipY = (input_b () & 0x00c0);

	timeNewY = get_capture (3);
	intervalY = timeNewY - timeOldY;
	stateCHAY = ~(((ipY & 0x80)>>4) ^ ((ipY & 0x40)>>5)) & 0x01;
	if ( (ipY & 0x80)>>7 == (ipY & 0x40)>>6 ) {
		directionReadY = 1;
		countDistanceY += 1;
	}
	else{
		directionReadY = 2;
		countDistanceY -= 1;
	}
	timeOldY = timeNewY;
	// computeInstantlyDistantY();

}

#INT_IC4
void testIC4()
{
	int16u ipY = (input_b () & 0x00c0);
	timeNewY = get_capture(4);

	intervalY = timeNewY - timeOldY;
	stateCHBY = ((ipY & 0x80)>>4) ^ ((ipY & 0x40)>>5);
	if ( (ipY & 0x80)>>7 != (ipY & 0x40)>>6 ){
		directionReadY = 1;
		countDistanceY += 1;
	}
	else{
		directionReadY = 2;
		countDistanceY -= 1;
	}

	timeOldY = timeNewY;
	// computeInstantlyDistantY();

}


/****************************************************************************/
/**                                                                        **/
/**                                 Interrupt Functions                                   **/
/**                                                                        **/
/****************************************************************************/

#INT_RDA
void RDA1()
{
	static FRAME_STATE FrameState = FRAME_WAIT;
	static int8u FrmIdx = 0;
	static int8u Lenght = 0;
	int8u Chr;
	int8u *errCode;
	Chr = getc();
	RxCount++;
	switch(FrameState)
	{
		case FRAME_WAIT:
			if(Chr == START_CHR)
			{
				RxBuffPtr[FrmIdx] = Chr;
				FrmIdx++;
				FrameState = FRAME_PROGRESS;
			}
			break;
		case  FRAME_PROGRESS:
			if(Chr == START_CHR)
			{
				RxBuffPtr[FrmIdx] = Chr;
				FrmIdx++;
				FrameState = FRAME_PROGRESS2;
			}
			else
			{
				FrmIdx = 0;
				FrameState = FRAME_WAIT;
			}
			break;
		case FRAME_PROGRESS2:
			if(FrmIdx == 2)
			{
				if(Chr == 0x01)
				// if(1)
				{
					RxBuffPtr[FrmIdx] = Chr;
					FrmIdx++;
				}
				else
				{
					FrmIdx = 0;
					FrameState = FRAME_WAIT;
				}	
			}
			else if(FrmIdx == 3)
			{
				RxBuffPtr[FrmIdx] = Chr;
				Lenght = Chr;
				FrmIdx++;
			}
			else if(FrmIdx < 3+Lenght)
			{
				RxBuffPtr[FrmIdx] = Chr;
				FrmIdx++;
			}
			else if(FrmIdx == 3+Lenght)
			{
				RxBuffPtr[FrmIdx] = Chr;
				FrmIdx = 0;
				Lenght = 0;
				Rx1FrameCount++;

				QPtrXPut(&Rx1QCB,(void *)RxBuffPtr, &errCode);
				if (errCode == Q_FULL)
				{
					/* code */
					free((void *)RxBuffPtr);
					MemCount--;
					Rx1QFullCount++;
				}
				FrameState = FRAME_WAIT;

				RxBuffPtr = (int8u *)malloc((sizeof (int8u)) * RX_CMND_FRM_LN);
				if(RxBuffPtr == (int8u *)NULL)
				{
					disable_interrupts(INT_RDA);
					MemFail++;
				}
				else
				{
					MemCount++;
				}
			}
			
			break;
		default:
			break;
	}
	return;
}

#INT_TBE
void TBE1ISR()
{
	int8u destChr;
	Q_ERR errCode;
	Q8UXGet (&Tx1QCB, &destChr,&errCode);
	if (errCode == Q_OK)
	{
		/* code */
		putc(destChr);
	}
	else
	{
		disable_interrupts(INT_TBE);
		Tx1Flag = TX1_READY;
	}
	return;
}

#INT_EXT2
void ResetX()
{
	MotorMovingX(0,BREAK);
	StateResetX = 0;
	countDistanceX = 0;
	currentDistanceX = 0;	
	// 
	speedX = 300;
	if(((input_b () & 0x08)>>3)>0)
	{
		// printf("FUCK X1");
		// disable_interrupts( INT_EXT1 );
		ext_int_edge(2, H_TO_L);
		StateMotorX = 0;
		StateBreakX = 1;
	}
	else
	{
		// printf("FUCK X0");
		ext_int_edge(2, L_TO_H);
		StateMotorX = 1;
		StateDirectionX = 0;
		// MotorMovingX(300, CCW);
	}

}

#INT_EXT1
void ResetY()
{
	MotorMovingY(0,BREAK);
	StateResetY = 0;
	countDistanceY = 0;
	currentDistanceY = 0;
	// ext_int_edge(2, L_TO_H);
	speedY = 500;
	if(((input_b () & 0x02)>>1)>0)
	{
		// disable_interrupts( INT_EXT2 );
		// printf("FUCK Y1");
		ext_int_edge(1, H_TO_L);
		StateMotorY = 0;
		StateBreakY = 1;
	}
	else
	{
		// printf("FUCK Y0");
		ext_int_edge(1, L_TO_H);
		// ext_int_edge(2, L_TO_H)
		StateMotorY = 1;
		StateDirectionY = 0;
		// StateMotorX = 1;
		// StateDirectionX = 0;
		// speedY = 500;
	}
}
// /****************************************************************************/
/**                                                                        **/
/**                                 EOF                                    **/
/**                                                                        **/
/***************************************************************************/