# Recommender dataset

This repo is part of recommender project. It contains code for creating dataset for further machine learning. Dataset will include articles parsed from [habr.com](habr.com) and file with calculated similarities for their pairs.

## Requirements

- Ubuntu >= 18.04
- Python >= 3.8

## Installation

If you are using *pip* run command below to install python dependencies.

```shell
pip3 install -r requirements.txt
```

If you are using *Pipenv* you can run command:

```shell
pipenv install
```

Also you need to install redis server:

```shell
sudo apt install redis-server
```

## Usage

Entrypoint is file *run.py*. For running programm in sertain mode you shoud run this in root directory.

```shell
python run.py <task>
```

where `task` represents current task.

For example if you want to parse link for further downloading you need run command:

```shell
python run.py parse_links
```

### Avalable tasks

If you want to create dataset from scratch, you need run all tasks consistently.

#### 1. *parse_links*

Task for getting list of article links and saving them to *redis*.

#### 2. *parse_articles*

Task for parsing articles and saving it on disk. Content for each article are saved in folder `data/texts` by name `{id}.txt` where `id` is  identification number of article. Besides in file `data/desc.json` are stored additional information such as topics and tags for each article. Articles are downloaded used `aiohttp` and parsed used `lxml`.

#### 3. *translate_tags*

Task for topics and tags for each article from russian to english. Package `deep-translator` is used for this.

#### 4. *filter_data*

Task for filtering dataset. Filtered dataset will contain articles if list of tags more then 8 and number of symbols is more than 2000. During this task file `data/desc_filtered.json` will be created.

#### 5. *calculate_similarity*

Task for generating final dataset which contains calculated similarities for pairs of articles. Firstly dataset is split into 3 parts for training, testing and validation. After that  every text calculate similarity for random two sentenses bty formula:

<img src="https://latex.codecogs.com/gif.latex?sim(s_1,&space;s_2)=0.7*sim_{\text{fasttext}}(s_1,&space;s_2)&space;&plus;&space;0.3*sim_{\text{bow}}(s_1,&space;s_2)"/>

where 

<img src="https://latex.codecogs.com/gif.latex?sim(s_1,&space;s_2)_{\text{fasttext}}=&space;\frac{1}{len(s_1)len(s_2)}\sum_{w\in&space;s_1}emb_{\text{fasttext}}(w)&space;\cdot&space;\sum_{w\in&space;s_2}emb_{\text{fasttext}}(w)"/>

<img src="https://latex.codecogs.com/gif.latex?sim(s_1,&space;s_2)_{\text{bow}}=&space;\sum_{w_i\in&space;s_1&space;\bigcup&space;s_2}e_{i}*I_{s_1}(w_i)&space;\cdot&space;\sum_{w_i\in&space;s_1&space;\bigcup&space;s_2}e_{i}*I_{s_2}(w_i)"/>

here 

<img src="https://latex.codecogs.com/gif.latex?x&space;\cdot&space;y"/> is dor product for vectors <img src="https://latex.codecogs.com/gif.latex?x" /> and <img src="https://latex.codecogs.com/gif.latex?y" />,

<img src="https://latex.codecogs.com/gif.latex?emb_{\text{fasttext}}(w)" /> is embedding vector, produced by fasttext embeddings from `gensim` package,

<img src="https://latex.codecogs.com/gif.latex?I_{s_1}(w_i)" /> - is equal 1 if sentence <img src="https://latex.codecogs.com/gif.latex?s_1" /> contains word <img src="https://latex.codecogs.com/gif.latex?w_i" /> and 0 if it not.

## Results

After completion of all tasks will be created
- folder `data/texts` which contains txt files with text of each article
- file `data/desc.json` with description of articles in dataset
- file `data/desc_filtered.json` with filtered description
- file `data/train.json` with dataset description for training. Contains list with ids of two articles and similarity calculated for them.
- file `data/test.json` same description as above for testing 
- file `data/val.json` same description as above for validation 
