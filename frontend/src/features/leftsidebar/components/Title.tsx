type Props = {
  title: string;
};

const Title = ({ title }: Props) => {
  return (
    <div className="px-6 pt-6 pb-4">
      <h2 className="text-lg font-semibold text-gray-800 leading-snug">
        {title}
      </h2>
    </div>
  );
};

export default Title;