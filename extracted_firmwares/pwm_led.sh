#!/bin/sh

PWM_LED_NUM=24
PWM_LED_GS=1 #12
MAX_BRIGHTNESS=`expr $((1<<$PWM_LED_GS)) - 1`

usage(){
        echo "$0 [on/off/round][brightness]"
        exit 1
}

led_onoff_control(){

        local i=`expr $PWM_LED_NUM - 1`
        local onoff=$1
        local pwm_br=$2

        echo 1 > /sys/class/leds/pwm_led_le/brightness
        echo 0 > /sys/class/leds/pwm_led_le/brightness

        while [ $i -ge 0 ]
        do
                local j=`expr $PWM_LED_GS - 1`

                while [ $j -ge 0 ]
                do
                        if [ $(($onoff & $((1<<$i)))) -gt 0 ] && [ $(($pwm_br & $((1<<$j)))) -gt 0 ]; then
                                echo 1 > /sys/class/leds/pwm_led_sdi/brightness
                                echo 1 > /sys/class/leds/pwm_led_clk/brightness
                                echo 0 > /sys/class/leds/pwm_led_clk/brightness
                                echo 0 > /sys/class/leds/pwm_led_sdi/brightness
                        else
                                echo 0 > /sys/class/leds/pwm_led_sdi/brightness
                                echo 1 > /sys/class/leds/pwm_led_clk/brightness
                                echo 0 > /sys/class/leds/pwm_led_clk/brightness
                        fi
                        j=`expr $j - 1`
                done

                i=`expr $i - 1`
        done

        echo 1 > /sys/class/leds/pwm_led_le/brightness
        echo 0 > /sys/class/leds/pwm_led_le/brightness
}
##################
# main program
##################

trap "got_signal" SIGINT

got_signal() {
 logger -s "LED GOT SIGINT, EXIT"

 # off
 led_onoff_control 0 0
 echo 1 > /sys/class/leds/pwm_led_oe/brightness

 exit 0
}

logger -s "LED RUN CMD: $1 $2"

if [ ! -n "$1" ];then
        usage
fi

if [ ! -n "$2" ] || [ "$2" -gt $MAX_BRIGHTNESS ];then
        br=$MAX_BRIGHTNESS
else
        br=$2
fi

case "$1" in
        off)
                led_onoff_control 0 0
                echo 1 > /sys/class/leds/pwm_led_oe/brightness
                ;;
        on)
                led_onoff_control 16777215 $br #0xffffff
                echo 0 > /sys/class/leds/pwm_led_oe/brightness
                ;;
        round)
                local k=0
                echo 0 > /sys/class/leds/pwm_led_oe/brightness
                while true
                do
                        echo 1 > /sys/class/leds/pwm_led_le/brightness
                        echo 0 > /sys/class/leds/pwm_led_le/brightness
                        led_onoff_control $((1<<$k)) $br
                        echo 1 > /sys/class/leds/pwm_led_le/brightness
                        echo 0 > /sys/class/leds/pwm_led_le/brightness
                        k=`expr $k + 1`
                        if [ "$k" -eq "$PWM_LED_NUM" ];then
                                break
                        fi
                done

                # off
                led_onoff_control 0 0
                echo 1 > /sys/class/leds/pwm_led_oe/brightness
	
                ;;
        *)
                usage
                ;;
esac

logger -s "LED EXIT"

