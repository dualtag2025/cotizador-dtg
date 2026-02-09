import { Stack } from 'expo-router';
import { NavigationIndependentTree } from '@react-navigation/native';

export default function RootLayout() {
  return (
    <NavigationIndependentTree>
      <Stack
        screenOptions={{
          headerShown: false,
        }}
      />
    </NavigationIndependentTree>
  );
}
