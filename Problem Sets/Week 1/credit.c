#include <cs50.h>
#include <math.h>
#include <stdio.h>

int main()
{
    long credit;
    long dup;
    int sum = 0, i = 0, len = 0;
    do
    {
        credit = get_long("Number: ");
        dup = credit;
        while (credit)
        {
            if (i % 2)
            { // iterate
                int tmp = 2 * (credit % 10);
                if (tmp > 9)
                    sum += (tmp % 10 + tmp / 10);
                else
                    sum += tmp;
            }
            else
            {
                sum += credit % 10;
            }
            credit = credit / 10;
            i++;
            len++;
        }
    }
    while (credit);
    if (sum % 10 == 0)
    { // can be valid
        // for amex
        long amex = dup / pow(10, 13);
        if ((amex == 34 || amex == 37) && (len == 15))
        {
            printf("AMEX\n");
            return 0;
        }

        // for mastercard
        long master = dup / pow(10, 14);
        if ((len == 16) && (master >= 51 && master <= 55))
        {
            printf("MASTERCARD\n");
            return 0;
        }

        // for VISA
        long visa = dup / pow(10, 12);
        if ((len == 16 || len == 13) && (visa == 4 || master / 10 == 4))
        {
            printf("VISA\n");
            return 0;
        }

        // if none passed
        printf("INVALID\n");
    }
    else
    {
        printf("INVALID\n");
    }
}
