#include <iostream>
#include "options.hpp"

namespace po = boost::program_options;

void Options::process(int argc, char *argv[])
{
	po::options_description desc("Allowed options");
	desc.add_options()
		("help", "produce help message")
		("width", po::value<int>(&width)->default_value(10),
		 "number of horizontal spaces on board")
		("height", po::value<int>(&height)->default_value(10),
		 "number of vertical spaces on board")
		;

	po::variables_map vm;
	po::store(po::parse_command_line(argc, argv, desc), vm);
	po::notify(vm);

	if (vm.count("help")) {
		std::cout << desc << std::endl;
	}
}
