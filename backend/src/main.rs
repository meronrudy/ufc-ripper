use clap::{App, Arg, SubCommand};
use ufcr_util::{
    app_util::is_container,
    config_util::{is_debug, load_config},
    net_util::init_server,
    rt_util::{ExitHandler, set_custom_panic},
    bin_util::download_videos_from_csv,
};

#[tokio::main]
async fn main() {
    set_custom_panic(true);

    // This needs to be here, so it would be the last thing that will be dropped
    let _exit_handler = if is_container() {
        None
    } else { 
        Some(ExitHandler)
    };

    #[cfg(target_os = "windows")]
    ufcr_libs::log_util::enable_win32_conhost_support();

    let matches = App::new("UFC Ripper")
        .version("1.0")
        .author("Author Name <author@example.com>")
        .about("UFC Ripper CLI")
        .subcommand(
            SubCommand::with_name("download-from-csv")
                .about("Download videos from a CSV file")
                .arg(
                    Arg::with_name("CSV")
                        .help("Path to the CSV file")
                        .required(true)
                        .index(1),
                ),
        )
        .get_matches();

    if let Some(matches) = matches.subcommand_matches("download-from-csv") {
        if let Some(csv_path) = matches.value_of("CSV") {
            download_videos_from_csv(csv_path).await.unwrap();
        }
    } else {
        start_ufcr().await;
    }
}

/// Initializes the configuration and starts the application process.
async fn start_ufcr() {
    load_config().await;
    set_custom_panic(is_debug());
    init_server().await;
}
