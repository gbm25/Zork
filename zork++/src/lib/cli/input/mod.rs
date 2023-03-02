use crate::project_model;
use clap::{Parser, Subcommand, ValueEnum};

/// [`CliArgs`] is the command line arguments parser
///
/// #Test
/// ```rust
/// use clap::Parser;
/// use zork::cli::input::{CliArgs, Command, CppCompiler};
///
/// let parser = CliArgs::parse_from(["", "-vv", "--clear-cache", "test"]);
/// assert_eq!(parser.command, Command::Test);
/// assert_eq!(parser.verbose, 2);
/// assert_eq!(parser.clear_cache, true);
///
// Create Template Project
/// let parser = CliArgs::parse_from(["", "new", "example", "--git", "--compiler", "clang"]);
/// assert_eq!(parser.command, Command::New{name: "example".to_owned(), git: true, compiler: CppCompiler::CLANG, template: "basic".to_owned()});
///
// Run autogenerated project
/// let parser = CliArgs::parse_from(["", "-vv", "run"]);
/// assert_eq!(parser.command, Command::Run);
/// ```
#[derive(Parser, Debug, Default)]
#[command(name = "Zork++")]
#[command(author = "Zero Day Code")]
#[command(version = "0.7.0")]
#[command(
    about = "Zork++ is a build system for modern C++ projects",
    long_about = "Zork++ is a project of Zero Day Code. Find us: https://github.com/zerodaycode/Zork"
)]
pub struct CliArgs {
    #[command(subcommand)]
    pub command: Command,

    #[arg(short, long, action = clap::ArgAction::Count, help="Zork++ maximum allowed verbosity level is: '-vv'")]
    pub verbose: u8,

    #[arg(short, long, help = "Removes all the entries stored in the cache")]
    pub clear_cache: bool,
}

/// [`Command`] -  The core enum commands
#[derive(Subcommand, Debug, PartialEq, Eq, Default)]
pub enum Command {
    /// Triggers the process that builds the project based on the config file directives
    #[default]
    Build,
    /// Performns a
    Run,
    /// Executes the tests under the specified directory in the config file
    Test,
    /// Creates a new template project
    New {
        #[arg(help = "Name of the new project")]
        name: String,
        #[arg(long, help = "Initialize a new local git repo")]
        git: bool,
        #[arg(long, default_value = "clang", help = "Which compiler to use")]
        compiler: CppCompiler,
        #[arg(
            long,
            default_value = "basic",
            help = "What configuration file template to use"
        )]
        template: String,
    },
}

/// [`CppCompiler`] The C++ compilers available within Zork++ as a command line argument for the `new` argument
/// TODO Possible future interesting on support the Intel's C++ compiler?
#[derive(ValueEnum, Copy, Clone, Debug, PartialEq, Eq)]
pub enum CppCompiler {
    CLANG,
    MSVC,
    GCC,
}

// Clippy warns to prefer implementing the From trait instead of Into.
// That would require that the project model know about cli details, which is ugly.
#[allow(clippy::from_over_into)]
impl Into<project_model::compiler::CppCompiler> for CppCompiler {
    fn into(self) -> project_model::compiler::CppCompiler {
        match self {
            CppCompiler::CLANG => project_model::compiler::CppCompiler::CLANG,
            CppCompiler::MSVC => project_model::compiler::CppCompiler::MSVC,
            CppCompiler::GCC => project_model::compiler::CppCompiler::GCC,
        }
    }
}
