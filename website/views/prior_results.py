from django.shortcuts import render

MATH_RES = [{
    "name": "Team Sweepstakes",
    "cols": ["Place", "Team Name", "Points"],
    "rows": [["1", "Texas Momentum A", "938.46"], ["2", "Cowconuts", "843.46"], ["3", "Random Math", "831.56"], ["4", "Motown All-Stars", "813.67"], ["5", "PRISMS Falcons", "791.65"], ["6", "Tin Man", "767.75"], ["7", "Lexington Alpha", "719.29"], ["8", "Florida Alligators", "678.51"], ["9", "MN Gold", "673.05"], ["10", "Tour Epines 1", "656.8"], ["11", "BISV Bobcats A", "640.92"], ["12", "Math Advance Team A", "630.4"], ["13", "Gunn US Grade Pepper Spray\u2122", "600.74"], ["14", "The Jigglypuff Dodged", "584.39"], ["15", "Random Math - Team B", "569.93"], ["16", "The Jigglypuff Attacked", "556.84"], ["17", "MHSProfessionalJobbers A", "555.64"], ["18", "Saratoga 1", "543.92"], ["19", "MA Boys", "528.52"], ["20", "Harker Omega", "528.09"]]
}, {
    "name": "Individual Sweepstakes",
    "cols": ["Place", "Name", "Team", "Points"],
    "rows": [["1", "Luke Robitaille", "Texas Momentum A", "205.72"], ["2", "Raymond Feng", "Cowconuts", "144.31"], ["3", "Nilay Mishra", "Random Math", "125.62"], ["4", "Gary Hu", "Math Advance Team C", "122.74"], ["5", "Kevin Min", "iodgvypribdt", "116.46"], ["6", "Albert Wang", "MA Boys", "116.37"], ["7", "Howard Dai", "Glenbrook North", "115.77"], ["8", "Mason Fang", "Cowconuts", "111.13"], ["9", "Jasen Penchev", "Bulgaria 1", "109.28"], ["10", "Sumedh Vangara", "Chair", "108.43"], ["11", "Rishabh Das", "Tin Man", "104.87"], ["12", "Linden Lee", "MN Gold", "104.74"], ["13", "Yichen Xiao", "PRISMS Falcons", "104.61"], ["14", "Sai Konkimalla", "Random Math - Team B", "103.82"], ["15", "Allan Yuan", "ur mom", "103.32"], ["16", "Shreyas Shrivastava", "Motown All-Stars", "103.1"], ["17", "Isaac Chen", "Math Advance Team A", "101.88"], ["18", "Karthik Vedula", "Florida Alligators", "101.54"], ["19", "Anthony Wang", "Saratoga 1", "101.16"], ["20", "Razzi Masroor", "Motown All-Stars", "100.75"], ["20", "Advaith Avadhanam", "Random Math", "100.75"]]
}, {
    "name": "TCS Round",
    "cols": ["Place", "Team Name", "Points"],
    "rows": [["1", "MN Gold", "260"], ["2", "The Jigglypuff Dodged", "257"], ["3", "Motown All-Stars", "230"], ["4", "BISV Bobcats A", "228"], ["4", "MHSProfessionalJobbers A", "228"], ["6", "Lexington Alpha", "224"], ["7", "Random Math", "221.5"], ["8", "Harker Omega", "214"], ["9", "University of Toronto Schools A", "210"], ["10", "Scarecrow", "208"]]
}, {
    "name": "Team Round",
    "cols": ["Place", "Team Name", "Points"],
    "rows": [["1", "Texas Momentum A", "176.6"], ["2", "Motown All-Stars", "172.49"], ["3", "PRISMS Falcons", "152.6"], ["4", "Cowconuts", "140.45"], ["5", "Lexington Alpha", "139.31"], ["6", "Tour Epines 1", "136.37"], ["7", "Tin Man", "135.62"], ["8", "MA Boys", "132.25"], ["9", "BISV Bobcats A", "131.56"], ["10", "Florida Alligators", "124.15"]]
}, {
    "name": "Algebra / Number Theory Div. 1",
    "cols": ["Place", "Name", "Team", "Points"],
    "rows": [["1", "Luke Robitaille", "Texas Momentum A", "50.93"], ["2", "Mason Fang", "Cowconuts", "46.71"], ["3", "Anthony Wang", "Saratoga 1", "44.08"], ["3", "Nilay Mishra", "Random Math", "44.08"], ["3", "Kavan Doctor", "Random Math", "44.08"], ["3", "Linden Lee", "MN Gold", "44.08"], ["3", "Howard Dai", "Glenbrook North", "44.08"], ["3", "Albert Wang", "MA Boys", "44.08"], ["3", "Derek Liu", "Tour Epines 1", "44.08"], ["10", "Jason Zhang", "Motown All-Stars", "39.77"]]
}, {
    "name": "Geometry Div. 1",
    "cols": ["Place", "Name", "Team", "Points"],
    "rows": [["1", "Luke Robitaille", "Texas Momentum A", "87.79"], ["2", "Raymond Feng", "Cowconuts", "58.86"], ["3", "Gary Hu", "Math Advance Team C", "58.2"], ["4", "Karthik Vedula", "Florida Alligators", "51.01"], ["5", "qian xu", "PRISMS Young Falcons", "48.25"], ["5", "Andrew Wen", "Cowconuts", "48.25"], ["5", "Kevin Min", "iodgvypribdt", "48.25"], ["5", "Rishabh Das", "Tin Man", "48.25"], ["9", "Albert Wang", "MA Boys", "47.72"], ["10", "Sai Konkimalla", "Random Math - Team B", "46.95"]]
}, {
    "name": "Combinatorics Div. 1",
    "cols": ["Place", "Name", "Team", "Points"],
    "rows": [["1", "Luke Robitaille", "Texas Momentum A", "67"], ["2", "Yichen Xiao", "PRISMS Falcons", "62.53"], ["3", "Jialai She", "Florida Alligators", "53.87"], ["3", "Jasen Penchev", "Bulgaria 1", "53.87"], ["5", "Shreyas Shrivastava", "Motown All-Stars", "53"], ["6", "Linden Lee", "MN Gold", "48.2"], ["7", "Nilay Mishra", "Random Math", "47.14"], ["7", "Raymond Feng", "Cowconuts", "47.14"], ["7", "Rishabh Das", "Tin Man", "47.14"], ["10", "Jeff Lin", "Lexington Alpha", "46.69"]]
}, {
    "name": "Algebra / Number Theory Div. 2",
    "cols": ["Place", "Name", "Team", "Points"],
    "rows": [["1", "Jonathan Du", "A Piece of Pi", "30.41"], ["2", "Miranda Wang", "RVMG Galileo", "25.67"], ["3", "Sounak Bagchi", "MCA", "21.69"], ["4", "Catherine Li", "Cowconuts", "21.61"], ["5", "Eric Wang", "Math Minds", "21.55"], ["6", "Tina Li", "Texas Momentum B", "21.01"], ["6", "Alon Ragoler", "The Planetarium <{O}>", "21.01"], ["6", "Liran Zhou", "Jericho High A", "21.01"], ["9", "William Zhang", "Harker Omega 2", "18.68"], ["10", "Aniketh Tummala", "Harker Omega 2", "18.44"]]
}, {
    "name": "Geometry Div. 2",
    "cols": ["Place", "Name", "Team", "Points"],
    "rows": [["1", "Liran Zhou", "Jericho High A", "26.53"], ["2", "Xuzhou Ren", "Los Tigres", "22.25"], ["3", "Rohan Garg", "Math Advance Team B", "21.25"], ["4", "Angel Hristov", "Bulgaria A", "17.88"], ["5", "Tanush Aggarwal", "Gunn Cayenne", "17.74"], ["6", "Ishani Agarwal", "Saratoga 1", "17.72"], ["7", "Hongning Wang", "The Planetarium <{O}>", "16.95"], ["7", "Alon Ragoler", "The Planetarium <{O}>", "16.95"], ["7", "Sargam Mondal", "RVMG Galileo", "16.95"], ["7", "Qi Huang", "A Piece of Pi", "16.95"], ["7", "Utkarsh Goyal", "The Jigglypuff Battled", "16.95"]]
}, {
    "name": "Combinatorics Div. 2",
    "cols": ["Place", "Name", "Team", "Points"],
    "rows": [["1", "Jonathan Du", "A Piece of Pi", "23.58"], ["2", "Hongning Wang", "The Planetarium <{O}>", "22.17"], ["2", "Andrew Hua", "Not Great Valley", "22.17"], ["4", "Perry Dai", "University of Toronto Schools B", "21.85"], ["4", "Nathan Cheng", "The Jigglypuff Dodged", "21.85"], ["6", "Nicholas Darosa", "Los Tigres", "18.43"], ["7", "Tina Li", "Texas Momentum B", "17.31"], ["7", "Owen Tang", "Smort Pickles", "17.31"], ["7", "Darren Su", "Gem State Spuds", "17.31"], ["7", "Petko Lazarov", "Bulgaria A", "17.31"], ["7", "Demira Nedeva", "Bulgaria A", "17.31"], ["7", "Angel Hristov", "Bulgaria A", "17.31"]]
}]

def sweepstakes_math_2022(request):
    return render(request, 'prior_results/math_2022.html', {
        'tables': MATH_RES
    })

PROGRAMMING_RES = [{
    "name": "Optimization Round",
    "cols": ["Team Name", "Score"],
    "rows": [["RedSuns", "100.00"], ["elmike", "85.41"], ["The Ducklings", "79.34"], ["Blufius", "75.60"], ["Coderlab", "52.35"], ["MN Orange", "52.01"], ["Edinasaurs", "49.10"], ["PAForces", "48.05"], ["ur mom", "46.90"], ["MAD?", "43.42"]]
}, {
    "name": "AI Round",
    "cols": ["Team Name", "Score"],
    "rows": [["CCA Team 0", "100.00"], ["HungryHippo", "97.64"], ["PRISMS 10", "96.98"], ["The Ducklings", "95.70"], ["MN Yellow", "94.30"], ["Amity Spartans", "93.30"], ["Chargers", "92.95"], ["Code Minds", "92.74"], ["MN Orange", "92.10"], ["MAD?", "91.51"]]
}, {
    "name": "Murder on the Panda Express (Optimization)",
    "cols": ["Team Name", "Score"],
    "rows": [["RedSuns", "100.00"], ["elmike", "90.71"], ["Coderlab", "68.45"], ["MN Orange", "68.37"], ["Edinasaurs", "68.37"], ["PAForces", "67.23"], ["ur mom", "67.17"], ["PRISMS 10", "64.56"], ["Blufius", "63.89"], ["The Ducklings", "62.66"]]
}, {
    "name": "Help I’m stuck in an IKEA and my only contact with the outside world is this problem title",
    "cols": ["Team Name", "Score"],
    "rows": [["RedSuns", "100.00"], ["The Ducklings", "97.13"], ["Blufius", "88.09"], ["elmike", "79.75"], ["Sleeping in Cereal 2", "73.76"], ["Coderlab", "35.17"], ["MN Orange", "34.56"], ["CarmelValleyRN", "30.56"], ["HelloAlgo", "28.87"], ["Edinasaurs", "28.53"]]
}, {
    "name": "TNTwentyXX",
    "cols": ["Team Name", "Score"],
    "rows": [["elmike", "100.00"], ["127.0.0.1", "94.90"], ["PHS Gamma", "94.63"], ["The Ducklings", "94.56"], ["Code Minds", "94.45"], ["Amity Spartans", "93.86"], ["Chargers", "93.74"], ["MN Orange", "92.99"], ["HelloAlgo", "92.70"], ["MAD?", "92.26"]]
}, {
    "name": "Non-fungible Greed Control",
    "cols": ["Team Name", "Score"],
    "rows": [["CCA Team 0", "100.00"], ["PRISMS 01", "97.36"], ["PRISMS 10", "96.48"], ["HungryHippo", "95.17"], ["Bulgaria A", "89.89"], ["MN Yellow", "88.08"], ["The Ducklings", "87.37"], ["Dogs are supiror", "86.42"], ["LexMACS Z", "86.37"], ["Pirates", "85.08"]]
}, {
    "name": "Murder on the Panda Express - Random Generator",
    "cols": ["Team Name", "Score"],
    "rows": [["RedSuns", "100.00"], ["elmike", "92.77"], ["MAD?", "85.88"], ["MN Yellow", "77.15"], ["Coderlab", "69.51"], ["HelloAlgo", "69.34"], ["MN Orange", "63.94"], ["Edinasaurs", "63.94"], ["Blufius", "63.47"], ["PRISMS 10", "61.59"]]
}, {
    "name": "Murder on the Panda Express - Circles Generator",
    "cols": ["Team Name", "Score"],
    "rows": [["elmike", "100.00"], ["RedSuns", "97.47"], ["The Ducklings", "94.78"], ["Coderlab", "87.46"], ["MN Orange", "80.44"], ["Edinasaurs", "80.44"], ["ur mom", "79.62"], ["Blufius", "67.77"], ["PAForces", "66.39"], ["MAD?", "61.49"]]
}, {
    "name": "Murder on the Panda Express - Path Generator",
    "cols": ["Team Name", "Score"],
    "rows": [["RedSuns", "100.00"], ["PRISMS 10", "87.19"], ["elmike", "77.08"], ["PAForces", "76.26"], ["MN Orange", "59.02"], ["Edinasaurs", "59.02"], ["Blufius", "58.83"], ["ur mom", "58.69"], ["nek", "57.50"], ["Pinehurst 0", "56.80"]]
}]

def sweepstakes_programming_2022(request):
    return render(request, 'prior_results/programming_2022.html', {
        'tables': PROGRAMMING_RES,
        'sweepstakes_cols': [
            "Team Name",
            "Score",
            "Competitors"
        ],
        'sweepstakes': [["The Ducklings", "100.00", "Valerie Kwek, Eugene Kwek, Marcus Y Kwek"], ["RedSuns", "96.88", "Bala Venkataraman, Aaron Zhu, Daniel Ye"], ["elmike", "96.78", "Bhaumik Mehta, Eric Wang"], ["Blufius", "91.00", "Dylan Epstein-Gross, Prabhas Kurapati"], ["MN Orange", "82.19", "Caleb Hultmann, Linden Lee, Prithvi Kaashyap"], ["Coderlab", "79.73", "Brian Yan, Steven Gu, Elliott Cheng"], ["PRISMS 10", "78.51", "Tongyu Lu, Bomin Wei"], ["PAForces", "78.38", "Yihao Huang, Davin Jeong, Yifan Kang"], ["Edinasaurs", "77.71", "Adwin Shi, Keerthi Kaashyap"], ["MAD?", "76.90", "Martin Kopchev, Atanas Dimitrov, Deyan Hadzhi-Manich"]],
    })