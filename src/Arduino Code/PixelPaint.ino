#include <LedControl.h>

#define DIN_PIN 11
#define CLK_PIN 13
#define CS_PIN 10

LedControl matrix = LedControl(DIN_PIN, CLK_PIN, CS_PIN, 1);

byte pattern[8];

void setup()
{
    Serial.begin(9600);

    matrix.shutdown(0, false);
    matrix.setIntensity(0, 8);
    matrix.clearDisplay(0);
}

void loop()
{
    if (Serial.available() >= 8)
    {
        for (byte row = 0; row < 8; row++)
        {
            pattern[row] = Serial.read();
        }

        drawPattern();
    }
}

void drawPattern()
{
    for (byte row = 0; row < 8; row++)
    {
        matrix.setRow(0, row, pattern[row]);
    }
}