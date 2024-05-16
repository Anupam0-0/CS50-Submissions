#include <cs50.h>
#include <ctype.h>
#include <math.h>
#include <stdio.h>
#include <string.h>

int count_letters(string text);
int count_words(string text);
int count_sentences(string text);
void print(int index);

int main(void)
{
    string text = get_string("Text: ");

    // Count the number of letters, words, and sentences in the text
    int letters = count_letters(text);
    int words = count_words(text);
    int sentences = count_sentences(text);

    float L = (float) letters / words * 100;
    float S = (float) sentences / words * 100;

    // Compute the Coleman-Liau index
    float cal = ((0.0588 * L) - (0.296 * S) - 15.8);
    int index = round(cal);

    // Print the grade level
    print(index);
}

int count_letters(string text)
{
    int count = 0;
    int n = strlen(text);
    for (int i = 0; i < n; i++)
    {
        if ((text[i] >= 'a' && text[i] <= 'z') || (text[i] >= 'A' && text[i] <= 'Z'))
            count++;
    }
    return count;
}

int count_words(string text)
{
    int count = 1;
    int n = strlen(text);
    for (int i = 0; i < n; i++)
    {
        if (text[i] == ' ')
            count++;
    }
    return count;
}

int count_sentences(string text)
{
    int sen = 0;
    int n = strlen(text);
    for (int i = 0; i < n; i++)
    {
        if (text[i] == '.' || text[i] == '!' || text[i] == '?')
            sen++;
    }
    return sen;
}

void print(int index)
{
    if (index < 1)
    {
        printf("Before Grade 1\n");
        return;
    }
    else if (index > 15)
    {
        printf("Grade 16+\n");
        return;
    }
    else
    {
        printf("Grade %d\n", index);
        return;
    }
}
