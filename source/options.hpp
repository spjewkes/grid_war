#include <boost/program_options.hpp>

class Options
{
public:
	Options(int argc, char *argv[]) { process(argc, argv); }
	~Options() {}

private:
	void process(int argc, char *argv[]);
};

