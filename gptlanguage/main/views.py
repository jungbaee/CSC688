OPEANAI_API_KEY = "USE YOUR OPENAI API HERE"

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseRedirect
import openai, json
#from langchain.chat_models import ChatOpenAI

from django.contrib import auth, messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from .models import Question, QuizResult
from .form import SignUpForm, QuestionForm

from django.utils import timezone

user_input = 'English'

# Create your views here.
def home(request):
    #Check to see if logging in
    if request.method =='POST' and not request.user.is_authenticated:
        username = request.POST['username']#from question.html "name"
        password = request.POST['password']#from qusetion.html "name"
        #authenticate
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You have been logged in!")
            return redirect('home')
        else:
            messages.success(request, "There was an error logging in, please try again...")
            return redirect('home')

    global user_input
    user_input = request.POST.get('language_selection')
    print("User input in home: " + str(user_input))
    return render(request, "main/home.html", {})

def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out...")
    return redirect('home')

def register_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            #authenticate and login
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "You have successfully registered")
            return redirect('home')
    else:
        form = SignUpForm()
        return render(request, "main/register.html", {'form' : form})
    return render(request, "main/register.html", {'form' : form})
    
def add_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "You have successfully added a question")
            return redirect('home')
    else:
        form = QuestionForm()
        return render(request, "main/addquestion.html", {'form' : form})
    return render(request, "main/addquestion.html", {'form' : form})

def show_question(request):
    # Set up the OpenAI API client
    openai.api_key = OPEANAI_API_KEY
    error = False
    lan = str(user_input)
    # Generate a question and four answers using the GPT-3 API
    print("The user input in show_question: " + lan)
    question_prompt = f"Ask another multiple choice question in the following form about {user_input}: What is the capital of France?; A) Berlin; B) Rome; C) Paris (correct); D) Amsterdam"
    
    if  lan == "German":
        question_prompt = f"Ask a different multiple choice question in the following form: Was machst ___ hier?; A) ich; B) euch; C) du (correct); D) wir"
    if lan == "한국어":
        question_prompt = f"이렇게 다른 질문을 해줘: 저는 사과 __ 먹어요; A) 는; B) 이; C) 를 (correct); D) 가" 

    #For davinci  	openai.Completion.create
    #For 3.5 turbo openai.ChatCompletion.create
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=question_prompt,
        max_tokens=2000,
        temperature=0.8,
    )

    try:
        print("inside the views.py show question try except block")
        print("ChatGPT raw response: " + str(response))
        question_and_answers = response["choices"][0]["text"]

        # Extract the question and answers from the generated text
        lines = question_and_answers.strip().split(";")
        question = lines[0]
        answers = lines[1:]
        print("QUESTION is: " + question)
        print("Answers: " + answers[0])
        print("Answers: " + answers[1])
        print("Answers: " + answers[2])
        print("Answers: " + answers[3])

        # Find the correct answer by searching for the answer that contains "(correct)"
        correct_answer = 0
        print("right before the for loop")
        for i, answer in enumerate(answers):
            print("Enumerating through the options" + str(i))
            if "(correct)" in answer:
                answers[i] = answers[i][0:-9]
                correct_answer = i + 1
                print("correct answer is: " + str(correct_answer))
                break

        context = {
            'question': question,
            'answer1': answers[0],
            'answer2': answers[1],
            'answer3': answers[2],
            'answer4': answers[3],
            'correct_answer': correct_answer,
        }
        print("Right after the context")
    except IndexError:
        error = True
        print(question_prompt)
        print("IndexError has occurred - VSCode")

    if not error:
        # Render the template with the question and answer data
        chatGPTQuestion = Question()
        chatGPTQuestion.question_prompt = lan
        chatGPTQuestion.question = question
        chatGPTQuestion.option1 = answers[0]
        chatGPTQuestion.option2 = answers[1]
        chatGPTQuestion.option3 = answers[2]
        chatGPTQuestion.option4 = answers[3]
        chatGPTQuestion.correct_option = correct_answer
        #chatGPTQuestion = Question.objects.create(question_prompt=lan, question=question, option1=answer[0],option2=answer[1],option3=answer[2],options4=answer[3],correct_option=correct_answer)
        chatGPTQuestion.save()

        print("rendered successfully")
        return render(request, 'main/question.html', context)
    else:
        return render(request, 'main/question.html', {
            'question': "Sorry, an error occured",
            'correct_answer': None,
        })
    
def stat(request):
    user = request.user
    # Fetch the user's quiz results
    quiz_results = QuizResult.objects.filter(user=user)

    context = {
        'quiz_results' : quiz_results
    }
    return render(request, "main/stat.html", context)

def show_all_questions(request):
    queryset = Question.objects.all()
    context = {
        'questions' : queryset
    }
    return render(request, 'main/showallquestions.html', context)

def quiz_from_database(request):
    queryset = Question.objects.filter(question_prompt=user_input).order_by('?')[:3]#change to 5 later
    questions_json = json.dumps(list(queryset.values()), ensure_ascii=False)
    user = request.user
    quiz_results = QuizResult.objects.filter(user=user)

    context = {
        'questions_json': questions_json,
        'questions' : queryset,
        'quiz_results' : quiz_results,
    }

    return render(request, 'main/quiz.html', context)

def update_quiz_results(request):
    print("in the update_quiz_results:before")
    if request.method == 'POST':
        user = request.user
        total_questions = int(request.POST.get('totalQuestions'))
        total_correct_answers = int(request.POST.get('totalCorrectAnswers'))
        total_incorrect_answers = int(request.POST.get('totalIncorrectAnswers'))

        print(total_correct_answers)
        print(total_incorrect_answers)

        quiz_result, created = QuizResult.objects.get_or_create(user=user)
        quiz_result.total_questions += total_questions
        quiz_result.correct_answers += total_correct_answers
        quiz_result.incorrect_answers += total_incorrect_answers
        quiz_result.score_percentage = quiz_result.correct_answers/quiz_result.total_questions*100
        quiz_result.save()

        return JsonResponse({'status': 'success'})
    else:
        print("POST method not used")
        return JsonResponse({'status': 'error'})
       