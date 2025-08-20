# The intital scope of the project is to get the market sentiment of any given stock name for one day or two days upto 30 days. 
## First we will just stick to one day. 
### THe flow of the project will be following. 

# given a stock name. 
## The program will search the news_api for the articles. 
### The title, url, source and datetime will be extracted
#### The extracted title and urls will be first filtered through the trusted sources list. 
##### The they will be sent to openai for the relevace. WHIHC WILL RETURN A LIST OF FILTERED ARTICLES
###### THIS LIST WILL GO TO FINBERT TO GENERATE THE SENTIMENT OF THE MARKET. 
###### This sentiment will be shown to the user or the researcher to depict the sentiment of last 24 hours for the market of that particular stock. 

# Next step will be to go thorught the sources and find the most dependable free sources and fetch the articles full content from them. 

#### That full content will then be processed to get more realistic and applicable market sentiment. 
# We will also use faiss for embedding to save the articles and sentiment for later usage. for example next day or a week later. 

# The initial project will focus on only 5 stocks. If we want more stocks for invertors or traders. We can create a list of stocks. However this will have to be running in the backend on predefined time interval to get the real time sentiment. 

### One more thing to consider is that NewsAPI has more than 5000 sources, but it only displays 100 sources per call per page. Find out more about how to extract the rest if not the rest then the most important ones. 